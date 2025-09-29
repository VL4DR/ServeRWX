import sys
sys.path.insert(1, '../scripts')

import random
import dataclasses
import collections.abc
import unicorn as uc
import keystone as ks
from server_defs import ServerWriteRequest, ServerStatus
from client_interface import ClientInterface
from test_communication import TestCommunication

# Memory region for the server binary including bss
CODE_SECTION_BASE = 0x40000000
CODE_SECTION_LENGTH = 0x1000

# Memory region for a small piece of code that calls the server logic
SERVER_CALL_CODE_SECTION_BASE = 0x41000000
SERVER_CALL_CODE_SECTION_LENGTH = 0x1000

# Memory region for a function to be called by the server
FUNCTION_CALL_CODE_SECTION_BASE = 0x42000000
FUNCTION_CALL_CODE_SECTION_LENGTH = 0x1000

# Memory region for testing data read/write
DATA_SECTION_BASE = 0x50000000
DATA_SECTION_LENGTH = 0x1000

# Memory region for placing the server request
SERVER_REQUEST_BASE = 0x51000000
SERVER_REQUEST_SIZE = 0x1000

# Memory region for placing the server response
SERVER_RESPONSE_BASE = 0x52000000
SERVER_RESPONSE_SIZE = 0x1000

# Memory region for emulation stack
STACK_SECTION_BASE = 0x60000000
STACK_SECTION_LENGTH = 0x1000

SERVER_MAX_DATA_SIZE = 0x100
SERVER_MAX_READ_SIZE = SERVER_MAX_DATA_SIZE
SERVER_MAX_WRITE_SIZE = SERVER_MAX_DATA_SIZE - ServerWriteRequest.sizeof()


MEMORY_MAPPINGS = [(CODE_SECTION_BASE, CODE_SECTION_LENGTH),
                   (SERVER_CALL_CODE_SECTION_BASE, SERVER_CALL_CODE_SECTION_LENGTH),
                   (FUNCTION_CALL_CODE_SECTION_BASE, FUNCTION_CALL_CODE_SECTION_LENGTH),
                   (DATA_SECTION_BASE, DATA_SECTION_LENGTH),
                   (SERVER_REQUEST_BASE, SERVER_REQUEST_SIZE),
                   (SERVER_RESPONSE_BASE, SERVER_RESPONSE_SIZE),
                   (STACK_SECTION_BASE, STACK_SECTION_LENGTH)]

@dataclasses.dataclass
class ArchSpecificDefs:
    emu : uc.Uc
    kstone : ks.Ks
    stack_pointer : int
    call_server_str : str
    add_4_params_function_str : str
    call_return_value_mask : int
    address_transform_func : collections.abc.Callable[[int], int]

def addr_to_thumb(address):
    return address | 1

ARCH_TO_ARCH_OBJECT_MAPPING = {
    'arm' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_ARM),
        ks.Ks(ks.KS_ARCH_ARM, ks.KS_MODE_ARM),
        uc.arm_const.UC_ARM_REG_SP,
        f"MOVW R12, #0; MOVT R12, {(CODE_SECTION_BASE >> 16) & 0xFFFF}; BLX R12",
        "ADD R0, R0, R1; ADD R0, R0, R2; ADD R0, R0, R3; BX LR",
        0xFFFFFFFF,
        None),
    'arm_thumb' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_THUMB),
        ks.Ks(ks.KS_ARCH_ARM, ks.KS_MODE_THUMB),
        uc.arm_const.UC_ARM_REG_SP,
        f"MOVW R12, {(CODE_SECTION_BASE & 0xFFFF) | 1}; MOVT R12, {(CODE_SECTION_BASE >> 16) & 0xFFFF}; BLX R12",
        "ADD R0, R1; ADD R0, R2; ADD R0, R3; BX LR",
        0xFFFFFFFF,
        addr_to_thumb),
    'aarch64' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_ARM64, uc.UC_MODE_ARM),
        ks.Ks(ks.KS_ARCH_ARM64, 0),
        uc.arm64_const.UC_ARM64_REG_SP,
        f"LDR X5, ={CODE_SECTION_BASE}; BLR X5",
        "ADD X0, X0, X1; ADD X0, X0, X2; ADD X0, X0, X3; RET",
        0xFFFFFFFFFFFFFFFF,
        None),
    'x86' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_X86, uc.UC_MODE_32),
        ks.Ks(ks.KS_ARCH_X86, ks.KS_MODE_32),
        uc.x86_const.UC_X86_REG_ESP,
        f"call {CODE_SECTION_BASE}",
        "mov eax, [esp + 4]; add eax, [esp + 8]; add eax, [esp + 12]; add eax, [esp + 16]; ret",
        0xFFFFFFFF,
        None),
    'x86_64' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_X86, uc.UC_MODE_64),
        ks.Ks(ks.KS_ARCH_X86, ks.KS_MODE_64),
        uc.x86_const.UC_X86_REG_RSP,
        f"call {CODE_SECTION_BASE}",
        "add rdi, rsi; add rdi, rdx; add rdi, rcx; mov rax, rdi; ret",
        0xFFFFFFFFFFFFFFFF,
        None),
    'mips' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_MIPS, uc.UC_MODE_MIPS32),
        ks.Ks(ks.KS_ARCH_MIPS, ks.KS_MODE_MIPS32),
        uc.mips_const.UC_MIPS_REG_SP,
        f"lui $t0, {(CODE_SECTION_BASE >> 16) & 0xFFFF}; ori $t0, $t0, {CODE_SECTION_BASE & 0xFFFF}; jalr $t0",
        "move $v0, $a0; add $v0, $v0, $a1; add $v0, $v0, $a2; add $v0, $v0, $a3; jr $ra",
        0xFFFFFFFF,
        None)
}


class EmulationTester:
    def __init__(self, server_binary_path : str, arch : str):
        if not arch in ARCH_TO_ARCH_OBJECT_MAPPING:
            raise ValueError("Invalid architecture specified!")
        
        self._arch_defs = ARCH_TO_ARCH_OBJECT_MAPPING[arch]

        with open(server_binary_path, 'rb') as f:
            server_binary = f.read()
        self._initialize_emulator(server_binary)

        test_communication = TestCommunication(self._arch_defs.emu, SERVER_REQUEST_BASE, SERVER_REQUEST_SIZE, SERVER_RESPONSE_BASE, SERVER_RESPONSE_SIZE)
        self._client = ClientInterface(test_communication, self._call_server, self, **{})
    

    def _initialize_emulator(self, server_binary : bytes) -> None:
        for (base_address, length) in MEMORY_MAPPINGS:
            self._arch_defs.emu.mem_map(base_address, length)
        
        self._arch_defs.emu.mem_write(CODE_SECTION_BASE, server_binary)
        self._arch_defs.emu.reg_write(self._arch_defs.stack_pointer, STACK_SECTION_BASE + STACK_SECTION_LENGTH)
        self._arch_defs.emu.mem_write(DATA_SECTION_BASE, random.randbytes(DATA_SECTION_LENGTH))
    

    def _call_server(self, dummy=None) -> None:
        jump_to_server = self._code_assemble(self._arch_defs.call_server_str, SERVER_CALL_CODE_SECTION_BASE)
        self._arch_defs.emu.mem_write(SERVER_CALL_CODE_SECTION_BASE, jump_to_server)
        self._arch_defs.emu.emu_start(self.transform_address(SERVER_CALL_CODE_SECTION_BASE), SERVER_CALL_CODE_SECTION_BASE + len(jump_to_server))


    def _code_assemble(self, code_str : str, base_address : int = 0):
        return self._arch_defs.kstone.asm(code_str, base_address, as_bytes=True)[0] 


    def client_read_memory(self, address : int, size : int) -> bytes:
        return self._client.read_memory(address, size)


    def client_write_memory(self, address : int, data : bytes) -> int:
        return self._client.write_memory(address, data)
    

    def client_call_function(self, address : int, arg1 : int = 0, arg2 : int = 0, arg3 : int = 0, arg4 : int = 0):
        return self._client.call_function(address, arg1, arg2, arg3, arg4)
    

    def emulator_read_memory(self, address : int, size : int) -> bytes:
        return self._arch_defs.emu.mem_read(address, size)


    def emulator_write_memory(self, address : int, data : bytes) -> None:
        self._arch_defs.emu.mem_write(address, data)


    def assemble_call_func_asm(self) -> bytes:
        return self._code_assemble(self._arch_defs.add_4_params_function_str)
    

    def get_call_return_value_mask(self) -> int:
        return self._arch_defs.call_return_value_mask
    
    
    def transform_address(self, address : int) -> int:
        if not self._arch_defs.address_transform_func is None:
            return self._arch_defs.address_transform_func(address)
        return address
    