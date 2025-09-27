import sys
sys.path.insert(1, '../scripts')

import argparse
import random
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

class EmulationTester:
    def __init__(self, server_binary_path : str):
        self._emu = uc.Uc(uc.UC_ARCH_X86, uc.UC_MODE_64)
        self._kstone = ks.Ks(ks.KS_ARCH_X86, ks.KS_MODE_64)

        with open(server_binary_path, 'rb') as f:
            server_binary = f.read()
        self._initialize_emulator(server_binary)

        test_communication = TestCommunication(self._emu, SERVER_REQUEST_BASE, SERVER_REQUEST_SIZE, SERVER_RESPONSE_BASE, SERVER_RESPONSE_SIZE)
        self._client = ClientInterface(test_communication, self._call_server, self, **{})
    

    def code_assemble(self, code_str, base_address=0):
        return self._kstone.asm(code_str, base_address, as_bytes=True)[0] 
    

    def _initialize_emulator(self, server_binary : bytes):
        for (base_address, length) in MEMORY_MAPPINGS:
            self._emu.mem_map(base_address, length)
        
        self._emu.mem_write(CODE_SECTION_BASE, server_binary)
        self._emu.reg_write(uc.x86_const.UC_X86_REG_RSP, STACK_SECTION_BASE + STACK_SECTION_LENGTH)
        self._emu.mem_write(DATA_SECTION_BASE, random.randbytes(DATA_SECTION_LENGTH))

        jump_to_server = self.code_assemble(f"call {CODE_SECTION_BASE}", SERVER_CALL_CODE_SECTION_BASE)
        self._emu.mem_write(SERVER_CALL_CODE_SECTION_BASE, jump_to_server)
    

    def _call_server(self, dummy=None):
        self._emu.emu_start(SERVER_CALL_CODE_SECTION_BASE, SERVER_CALL_CODE_SECTION_BASE + 5)


    def code_assemble(self, code_str, base_address=0):
        return self._kstone.asm(code_str, base_address, as_bytes=True)[0] 


    def client_read_memory(self, address : int, size : int) -> bytes:
        return self._client.read_memory(address, size)


    def client_write_memory(self, address : int, data : bytes):
        return self._client.write_memory(address, data)
    

    def client_call_function(self, address : int, arg1 : int = 0, arg2 : int = 0, arg3 : int = 0, arg4 : int = 0):
        return self._client.call_function(address, arg1, arg2, arg3, arg4)
    

    def emulator_read_memory(self, address : int, size : int) -> bytes:
        return self._emu.mem_read(address, size)


    def emulator_write_memory(self, address : int, data : bytes):
        self._emu.mem_write(address, data)
