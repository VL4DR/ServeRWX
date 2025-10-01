import sys
sys.path.insert(1, '../scripts')

import random
import pytest
import server_defs
import emulation_tester as et

@pytest.fixture(scope='session')
def tester(pytestconfig):
    print("FIXTURE CALLED!")
    server_binary_path = pytestconfig.getoption("server_binary_path")
    arch = pytestconfig.getoption('arch')
    tester = et.EmulationTester(server_binary_path, arch)
    return tester


def test_invalid_magic(tester : et.EmulationTester):
    response_header, _ = tester.send_receive_raw_request(server_defs.DEFAULT_MAGIC + 1,
                                                server_defs.ServerOpcode.SERVER_OPCODE_NOP.value,
                                                0)
    
    assert response_header.status == server_defs.ServerStatus.SERVER_INVALID_MAGIC.value


def test_read_sanity(tester : et.EmulationTester):
    status, response_data_bytes = tester.client_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_DATA_SIZE)

    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value
    assert response_data_bytes == tester.emulator_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_DATA_SIZE)


def test_read_too_large_size(tester : et.EmulationTester):
    status, _ = tester.client_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_READ_SIZE + 1)
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_read_zero_size(tester : et.EmulationTester):
    status, _ =  tester.client_read_memory(et.DATA_SECTION_BASE, 0)
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_read_invalid_request_length(tester : et.EmulationTester):
    read_request_length = server_defs.ServerReadRequest.sizeof()
    response_header, _ = tester.send_receive_raw_request(server_defs.DEFAULT_MAGIC,
                                                server_defs.ServerOpcode.SERVER_OPCODE_READ.value,
                                                read_request_length + 1,
                                                data=b'\x00' * (read_request_length + 1))
    
    assert response_header.status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_write_sanity(tester : et.EmulationTester):
    data_to_write = random.randbytes(et.SERVER_MAX_WRITE_SIZE)
    status = tester.client_write_memory(et.DATA_SECTION_BASE, data_to_write)
    
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value
    assert data_to_write == tester.emulator_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_WRITE_SIZE)


def test_write_too_large_size(tester : et.EmulationTester):
    data_to_write = random.randbytes(et.SERVER_MAX_WRITE_SIZE + 1)
    original_data = tester.emulator_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_WRITE_SIZE + 1)

    status = tester.client_write_memory(et.DATA_SECTION_BASE, data_to_write)

    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value
    assert original_data == tester.emulator_read_memory(et.DATA_SECTION_BASE, et.SERVER_MAX_WRITE_SIZE + 1)


def test_write_zero_size(tester : et.EmulationTester):
    data_to_write = b''

    status = tester.client_write_memory(et.DATA_SECTION_BASE, data_to_write)

    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_call_sanity(tester : et.EmulationTester):
    func_bytes = tester.assemble_call_func_asm()
    tester.emulator_write_memory(et.FUNCTION_CALL_CODE_SECTION_BASE, func_bytes)
    status, response_data_bytes = tester.client_call_function(tester.transform_address(et.FUNCTION_CALL_CODE_SECTION_BASE), 0x1000, 0x1500, 0x2000, 0x3000)

    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value
    assert len(response_data_bytes) == 8
    assert (int.from_bytes(response_data_bytes, 'little') & tester.get_call_return_value_mask()) == 0x7500


def test_call_invalid_request_length(tester : et.EmulationTester):
    call_request_length = server_defs.ServerCallRequest.sizeof()
    response_header, _ = tester.send_receive_raw_request(server_defs.DEFAULT_MAGIC,
                                                server_defs.ServerOpcode.SERVER_OPCODE_CALL.value,
                                                call_request_length + 1,
                                                data=b'\x00' * (call_request_length + 1))
    
    assert response_header.status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_initiate_transfer_invalid_request_length(tester : et.EmulationTester):
    status = tester.client_reset_state()
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    initiate_transfer_request_length = server_defs.ServerTransferInitiateRequest.sizeof()
    response_header, _ = tester.send_receive_raw_request(server_defs.DEFAULT_MAGIC,
                                                         server_defs.ServerOpcode.SERVER_OPCODE_TRANSFER_INITIATE.value,
                                                         initiate_transfer_request_length + 1,
                                                         data=b'\x01' * (initiate_transfer_request_length + 1))
    
    assert response_header.status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_initiate_transfer_zero_size(tester : et.EmulationTester):
    status = tester.client_reset_state()
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status = tester.client_initiate_data_transfer(0)

    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_data_transfer_offset_beyond_bounds(tester : et.EmulationTester):
    shellcode_size = 0x100
    status = tester.client_reset_state()
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status = tester.client_initiate_data_transfer(shellcode_size)

    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status = tester.client_transfer_data(shellcode_size + 1, b"\x00")

    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_data_transfer_chunk_overflow(tester : et.EmulationTester):
    shellcode_size = 0x100
    status = tester.client_reset_state()
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status = tester.client_initiate_data_transfer(shellcode_size)

    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status = tester.client_transfer_data(0, b"\x00" * (shellcode_size + 1))

    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_data_transfer_before_initiate(tester : et.EmulationTester):
    status = tester.client_reset_state()
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    chunk_size = et.SERVER_MAX_DATA_SIZE - server_defs.ServerTransferDataRequest.sizeof()
    status = tester.client_transfer_data(0, b"\x00" * chunk_size)

    assert status == server_defs.ServerStatus.SERVER_INVALID_STATE.value


def test_data_transfer_too_large_size(tester : et.EmulationTester):
    status = tester.client_reset_state()
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    max_chunk_size = et.SERVER_MAX_DATA_SIZE - server_defs.ServerTransferDataRequest.sizeof()
    shellcode_size = 2 * max_chunk_size
    status = tester.client_initiate_data_transfer(shellcode_size)

    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status = tester.client_transfer_data(0, b"\x00" * (max_chunk_size + 1))

    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_execute_before_initiate(tester : et.EmulationTester):
    status = tester.client_reset_state()
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status, _ = tester.client_call_shellcode()

    assert status == server_defs.ServerStatus.SERVER_INVALID_STATE.value


def test_shellcode_execute_sanity(tester : et.EmulationTester):
    status = tester.client_reset_state()
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value
    
    func_bytes = b"\x00\x00\x00\x00" * 200 + b"\x00\x00\x9f\xe5\x1e\xff\x2f\xe1\xef\xbe\xad\xde"
    status, response_data_bytes = tester.client_execute_shellcode_binary(func_bytes)

    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value
    assert (int.from_bytes(response_data_bytes, 'little') & tester.get_call_return_value_mask()) == 0xDEADBEEF
