import sys
sys.path.insert(1, '../scripts')

import dataclasses
import collections
import unicorn as uc
import keystone as ks
import server_defs


# A storage class that holds architecture-specific definitions so that the server can be tested
# on multiple architectures.
@dataclasses.dataclass
class ArchSpecificDefs:
    # The emulator object that will be used to emulate the server's functionality.
    emu : uc.Uc
    # The assembler object that will be used to assemble architecture-specific
    # code.
    assembler : ks.Ks
    # The stack pointer identifier which is used by the emulator.
    stack_pointer : int
    # The assembly code (not binary!) that is used to invoke the
    # test server's entry point.
    call_server_str : str
    # The assembly code (not binary!) for a function that will be used as
    # the test function for the function call feature (in this case, the function
    # adds its 4 parameters and returns the result).
    add_4_params_function_str : str
    # As different architectures have different register width, this mask is used
    # to filter out the higher-order bits from the result returned from called functions.
    call_return_value_mask : int
    # The conversion function that given an address, returns an address appropriate
    # for execution. Currently, this function is only applicable to ARM code running in Thumb mode,
    # which requires the LSB bit of the address to be on before starting execution from that address.
    address_transform_func : collections.abc.Callable[[int], int]
    # The assembly code (not binary!) for a shellcode to be executed on the server. In this case,
    # the function simply returns a magic value for 0xAABBCCDDCAFEBABE (or just the lower 32-bits of this
    # magic, namely 0xCAFEBABE, for architectures that usually return a 32-bit value).
    test_shellcode_str : str

# Memory region for the server binary including bss
CODE_SECTION_BASE = 0x40000000
CODE_SECTION_LENGTH = 0x2000

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

SERVER_MAX_DATA_SIZE = server_defs.DEFAULT_MAX_SERVER_DATA_SIZE
SERVER_MAX_READ_SIZE = SERVER_MAX_DATA_SIZE
SERVER_MAX_WRITE_SIZE = server_defs.DEFAULT_MAX_SERVER_DATA_SIZE - server_defs.ServerWriteRequest.sizeof()


MEMORY_MAPPINGS = [(CODE_SECTION_BASE, CODE_SECTION_LENGTH),
                   (SERVER_CALL_CODE_SECTION_BASE, SERVER_CALL_CODE_SECTION_LENGTH),
                   (FUNCTION_CALL_CODE_SECTION_BASE, FUNCTION_CALL_CODE_SECTION_LENGTH),
                   (DATA_SECTION_BASE, DATA_SECTION_LENGTH),
                   (SERVER_REQUEST_BASE, SERVER_REQUEST_SIZE),
                   (SERVER_RESPONSE_BASE, SERVER_RESPONSE_SIZE),
                   (STACK_SECTION_BASE, STACK_SECTION_LENGTH)]


ARCH_TO_ARCH_OBJECT_MAPPING = {
    'arm' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_ARM),
        ks.Ks(ks.KS_ARCH_ARM, ks.KS_MODE_ARM),
        uc.arm_const.UC_ARM_REG_SP,
        f"MOVW R12, #0; MOVT R12, {(CODE_SECTION_BASE >> 16) & 0xFFFF}; BLX R12",
        "ADD R0, R0, R1; ADD R0, R0, R2; ADD R0, R0, R3; BX LR",
        0xFFFFFFFF,
        None,
        "LDR R0, =0xCAFEBABE; BX LR"),
    'arm_thumb' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_THUMB),
        ks.Ks(ks.KS_ARCH_ARM, ks.KS_MODE_THUMB),
        uc.arm_const.UC_ARM_REG_SP,
        f"MOVW R12, {(CODE_SECTION_BASE & 0xFFFF) | 1}; MOVT R12, {(CODE_SECTION_BASE >> 16) & 0xFFFF}; BLX R12",
        "ADD R0, R1; ADD R0, R2; ADD R0, R3; BX LR",
        0xFFFFFFFF,
        lambda address : address | 1,
        "LDR R0, =0xCAFEBABE; BX LR"),
    'aarch64' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_ARM64, uc.UC_MODE_ARM),
        ks.Ks(ks.KS_ARCH_ARM64, 0),
        uc.arm64_const.UC_ARM64_REG_SP,
        f"LDR X5, ={CODE_SECTION_BASE}; BLR X5",
        "ADD X0, X0, X1; ADD X0, X0, X2; ADD X0, X0, X3; RET",
        0xFFFFFFFFFFFFFFFF,
        None,
        "LDR X0, =0xAABBCCDDCAFEBABE; RET"),
    'x86' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_X86, uc.UC_MODE_32),
        ks.Ks(ks.KS_ARCH_X86, ks.KS_MODE_32),
        uc.x86_const.UC_X86_REG_ESP,
        f"call {CODE_SECTION_BASE}",
        "mov eax, [esp + 4]; add eax, [esp + 8]; add eax, [esp + 12]; add eax, [esp + 16]; ret",
        0xFFFFFFFF,
        None,
        "mov eax, 0xCAFEBABE; ret"),
    'x86_64' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_X86, uc.UC_MODE_64),
        ks.Ks(ks.KS_ARCH_X86, ks.KS_MODE_64),
        uc.x86_const.UC_X86_REG_RSP,
        f"call {CODE_SECTION_BASE}",
        "add rdi, rsi; add rdi, rdx; add rdi, rcx; mov rax, rdi; ret",
        0xFFFFFFFFFFFFFFFF,
        None,
        "mov rax, 0xAABBCCDDCAFEBABE; ret"),
    'mips' : ArchSpecificDefs(
        uc.Uc(uc.UC_ARCH_MIPS, uc.UC_MODE_MIPS32),
        ks.Ks(ks.KS_ARCH_MIPS, ks.KS_MODE_MIPS32),
        uc.mips_const.UC_MIPS_REG_SP,
        f"lui $t9, {(CODE_SECTION_BASE >> 16) & 0xFFFF}; ori $t9, $t9, {CODE_SECTION_BASE & 0xFFFF}; jalr $t9; nop",
        "move $v0, $a0; add $v0, $v0, $a1; add $v0, $v0, $a2; add $v0, $v0, $a3; jr $ra",
        0xFFFFFFFF,
        None,
        "lui $v0, 0xCAFE; ori $v0, $v0, 0xBABE; jr $ra")
}
