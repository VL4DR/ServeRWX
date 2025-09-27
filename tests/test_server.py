import sys
sys.path.insert(1, '../scripts')

import random
import pytest
from server_defs import ServerWriteRequest, ServerStatus
import emulation_tester as et

@pytest.fixture(scope='session')
def tester(pytestconfig):
    server_binary_path = pytestconfig.getoption("server_binary_path")
    if server_binary_path is None:
        pytest.skip()
    return et.EmulationTester(server_binary_path)

def test_read_sanity(tester : et.EmulationTester):
    status, response_data_bytes = tester.client_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_DATA_SIZE)

    assert status == ServerStatus.SERVER_SUCCESS.value
    assert response_data_bytes == tester.emulator_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_DATA_SIZE)


def test_read_too_large_length(tester : et.EmulationTester):
    status, _ = tester.client_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_READ_SIZE + 1)
    assert status == ServerStatus.SERVER_INVALID_PARAMETER.value


def test_read_zero_length(tester : et.EmulationTester):
    status, _ =  tester.client_read_memory(et.DATA_SECTION_BASE, 0)
    assert status == ServerStatus.SERVER_INVALID_PARAMETER.value


def test_write_sanity(tester : et.EmulationTester):
    data_to_write = random.randbytes(et.SERVER_MAX_WRITE_SIZE)
    status = tester.client_write_memory(et.DATA_SECTION_BASE, data_to_write)
    
    assert status == ServerStatus.SERVER_SUCCESS.value
    assert data_to_write == tester.emulator_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_WRITE_SIZE)


def test_write_too_large_length(tester : et.EmulationTester):
    data_to_write = random.randbytes(et.SERVER_MAX_WRITE_SIZE + 1)
    original_data = tester.emulator_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_WRITE_SIZE + 1)

    status = tester.client_write_memory(et.DATA_SECTION_BASE, data_to_write)

    assert status == ServerStatus.SERVER_INVALID_PARAMETER.value
    assert original_data == tester.emulator_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_WRITE_SIZE + 1)


def test_write_zero_length(tester : et.EmulationTester):
    data_to_write = b''

    status = tester.client_write_memory(et.DATA_SECTION_BASE, data_to_write)

    assert status == ServerStatus.SERVER_INVALID_PARAMETER.value


def test_call_sanity(tester : et.EmulationTester):
    func_bytes = tester.code_assemble("add rdi, rsi; add rdi, rdx; add rdi, rcx; mov rax, rdi; ret")
    tester.emulator_write_memory(et.FUNCTION_CALL_CODE_SECTION_BASE, func_bytes)
    status, response_data_bytes = tester.client_call_function(et.FUNCTION_CALL_CODE_SECTION_BASE, 0x1000, 0x1500, 0x2000, 0x3000)

    assert status == ServerStatus.SERVER_SUCCESS.value
    assert len(response_data_bytes) == 8
    assert int.from_bytes(response_data_bytes, 'little') == 0x7500
