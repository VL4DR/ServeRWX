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

SERVER_MAX_DATA_SIZE = 0x200
SERVER_MAX_READ_SIZE = SERVER_MAX_DATA_SIZE
SERVER_MAX_WRITE_SIZE = SERVER_MAX_DATA_SIZE - ServerWriteRequest.sizeof()


MEMORY_MAPPINGS = [(CODE_SECTION_BASE, CODE_SECTION_LENGTH), # Memory mapping for code
                   (SERVER_CALL_CODE_SECTION_BASE, SERVER_CALL_CODE_SECTION_LENGTH),
                   (FUNCTION_CALL_CODE_SECTION_BASE, FUNCTION_CALL_CODE_SECTION_LENGTH),
                   (DATA_SECTION_BASE, DATA_SECTION_LENGTH), # Memory mapping for data
                   (SERVER_REQUEST_BASE, SERVER_REQUEST_SIZE),
                   (SERVER_RESPONSE_BASE, SERVER_RESPONSE_SIZE),
                   (STACK_SECTION_BASE, STACK_SECTION_LENGTH)] # Memory mapping for stack


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("server_binary_path", type=str, help='path to server flat binary')

    return parser.parse_args()


def initialize_emulator(emu, kstone, server_binary):
    for (base_address, length) in MEMORY_MAPPINGS:
        emu.mem_map(base_address, length)
    
    emu.mem_write(CODE_SECTION_BASE, server_binary)
    emu.reg_write(uc.x86_const.UC_X86_REG_RSP, STACK_SECTION_BASE + STACK_SECTION_LENGTH)
    emu.mem_write(DATA_SECTION_BASE, random.randbytes(DATA_SECTION_LENGTH))

    jump_to_server = code_assemble(kstone, f"call {CODE_SECTION_BASE}", SERVER_CALL_CODE_SECTION_BASE)
    emu.mem_write(SERVER_CALL_CODE_SECTION_BASE, jump_to_server)


def code_assemble(kstone, code_str, base_address=0):
    return kstone.asm(code_str, base_address, as_bytes=True)[0]


def test_read_sanity(client : ClientInterface, emu):
    status, response_data_bytes = client.read_memory(DATA_SECTION_BASE, SERVER_MAX_READ_SIZE)

    assert status == ServerStatus.SERVER_SUCCESS.value
    assert response_data_bytes == emu.mem_read(DATA_SECTION_BASE, SERVER_MAX_READ_SIZE)


def test_read_too_large_length(client : ClientInterface):
    status, _ = client.read_memory(DATA_SECTION_BASE, SERVER_MAX_READ_SIZE + 1)
    assert status == ServerStatus.SERVER_INVALID_PARAMETER.value


def test_read_zero_length(client : ClientInterface):
    status, _ =  client.read_memory(DATA_SECTION_BASE, 0)
    assert status == ServerStatus.SERVER_INVALID_PARAMETER.value


def test_write_sanity(client : ClientInterface, emu):
    data_to_write = random.randbytes(SERVER_MAX_WRITE_SIZE)
    status = client.write_memory(DATA_SECTION_BASE, data_to_write)
    
    assert status == ServerStatus.SERVER_SUCCESS.value
    assert data_to_write == emu.mem_read(DATA_SECTION_BASE, SERVER_MAX_WRITE_SIZE)


def test_write_too_large_length(client : ClientInterface, emu):
    data_to_write = random.randbytes(SERVER_MAX_WRITE_SIZE + 1)
    original_data = emu.mem_read(DATA_SECTION_BASE, SERVER_MAX_WRITE_SIZE + 1)

    status = client.write_memory(DATA_SECTION_BASE, data_to_write)

    assert status == ServerStatus.SERVER_INVALID_PARAMETER.value
    assert original_data == emu.mem_read(DATA_SECTION_BASE, SERVER_MAX_WRITE_SIZE + 1)


def test_write_zero_length(client : ClientInterface, emu):
    data_to_write = b''

    status = client.write_memory(DATA_SECTION_BASE, data_to_write)

    assert status == ServerStatus.SERVER_INVALID_PARAMETER.value


def test_call_sanity(client : ClientInterface, emu, ks):
    func_bytes = code_assemble(ks, "add rdi, rsi; add rdi, rdx; add rdi, rcx; mov rax, rdi; ret")
    emu.mem_write(FUNCTION_CALL_CODE_SECTION_BASE, func_bytes)
    status, response_data_bytes = client.call_function(FUNCTION_CALL_CODE_SECTION_BASE, 0x1000, 0x1500, 0x2000, 0x3000)

    assert status == ServerStatus.SERVER_SUCCESS.value
    assert len(response_data_bytes) == 8
    assert int.from_bytes(response_data_bytes, 'little') == 0x7500


def main(args):

    emu = uc.Uc(uc.UC_ARCH_X86, uc.UC_MODE_64)
    kstone = ks.Ks(ks.KS_ARCH_X86, ks.KS_MODE_64)

    with open(args.server_binary_path, 'rb') as f:
        server_binary = f.read()

    initialize_emulator(emu, kstone, server_binary)
    test_communication = TestCommunication(emu, SERVER_REQUEST_BASE, SERVER_REQUEST_SIZE, SERVER_RESPONSE_BASE, SERVER_RESPONSE_SIZE)
    client = ClientInterface(test_communication, **{})
    
    test_read_sanity(client)
    test_read_too_large_length(client)
    test_read_zero_length(client)
    test_write_sanity(client)
    test_write_too_large_length(client)
    test_write_zero_length(client)
    test_call_sanity(client, kstone)


if __name__ == "__main__":
    args = parse_args()
    main(args)