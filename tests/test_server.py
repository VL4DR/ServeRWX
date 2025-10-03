import sys
sys.path.insert(1, '../scripts')

import random
import pytest
import server_defs
import emulation_tester_defs as emu_test_defs
import emulation_tester as et

@pytest.fixture(scope='session')
def tester_session_resource(pytestconfig):
    server_binary_path = pytestconfig.getoption("server_binary_path")
    arch = pytestconfig.getoption('arch')
    yield et.EmulationTester(server_binary_path, arch)


@pytest.fixture(scope='function')
def tester(tester_session_resource : et.EmulationTester):
    tester_session_resource.client_reset_state()
    yield tester_session_resource


def test_invalid_magic(tester : et.EmulationTester):
    """
    Test the expected server response when an invalid magic is provided within the request.
    """
    response_header, _ = tester.send_receive_raw_request(server_defs.DEFAULT_MAGIC + 1,
                                                server_defs.ServerOpcode.SERVER_OPCODE_NOP.value,
                                                0)
    assert response_header.status == server_defs.ServerStatus.SERVER_INVALID_MAGIC.value


def test_read_sanity(tester : et.EmulationTester):
    """
    Test that reading arbitrary memory works as expected.
    """
    status, response_data_bytes = tester.client_read_memory(emu_test_defs.DATA_SECTION_BASE,
                                                            emu_test_defs.SERVER_MAX_DATA_SIZE)
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value
    assert response_data_bytes == tester.emulator_read_memory(emu_test_defs.DATA_SECTION_BASE,
                                                              emu_test_defs.SERVER_MAX_DATA_SIZE)


def test_read_too_large_size(tester : et.EmulationTester):
    """
    Test the expected server response when there's an attempt to read more bytes than the server
    supports in a single request.
    """
    status, _ = tester.client_read_memory(emu_test_defs.DATA_SECTION_BASE,
                                          emu_test_defs.SERVER_MAX_READ_SIZE + 1)
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_read_zero_size(tester : et.EmulationTester):
    """
    Test the expected server response when a read of 0 bytes is requested.
    """
    status, _ =  tester.client_read_memory(emu_test_defs.DATA_SECTION_BASE, 0)
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_read_invalid_request_length(tester : et.EmulationTester):
    """
    Test the expected server response when an incorrect request size is provided
    in the request header for reading arbitrary memory.
    """
    read_request_length = server_defs.ServerReadRequest.sizeof()
    response_header, _ = tester.send_receive_raw_request(server_defs.DEFAULT_MAGIC,
                                                server_defs.ServerOpcode.SERVER_OPCODE_READ.value,
                                                read_request_length + 1,
                                                data=b'\x00' * (read_request_length + 1))
    assert response_header.status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_write_sanity(tester : et.EmulationTester):
    """
    Test that writing to arbitrary memory works as expected.
    """
    data_to_write = random.randbytes(emu_test_defs.SERVER_MAX_WRITE_SIZE)
    status = tester.client_write_memory(emu_test_defs.DATA_SECTION_BASE, data_to_write)
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value
    assert data_to_write == tester.emulator_read_memory(emu_test_defs.DATA_SECTION_BASE,
                                                        emu_test_defs.SERVER_MAX_WRITE_SIZE)


def test_write_too_large_size(tester : et.EmulationTester):
    """
    Test the expected server response when there's an attempt to write more bytes than the server
    supports in a single request.
    """
    data_to_write = random.randbytes(emu_test_defs.SERVER_MAX_WRITE_SIZE + 1)
    original_data = tester.emulator_read_memory(emu_test_defs.DATA_SECTION_BASE,
                                                emu_test_defs.SERVER_MAX_WRITE_SIZE + 1)

    status = tester.client_write_memory(emu_test_defs.DATA_SECTION_BASE, data_to_write)
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value
    assert original_data == tester.emulator_read_memory(emu_test_defs.DATA_SECTION_BASE,
                                                        emu_test_defs.SERVER_MAX_WRITE_SIZE + 1)


def test_write_zero_size(tester : et.EmulationTester):
    """
    Test the expected server response when a write of 0 bytes is requested.
    """
    data_to_write = b''

    status = tester.client_write_memory(emu_test_defs.DATA_SECTION_BASE, data_to_write)
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_call_sanity(tester : et.EmulationTester):
    """
    Test that calling an arbitrary function works as expected.
    """
    func_bytes = tester.assemble_call_func_asm()
    transformed_address = tester.transform_address(emu_test_defs.FUNCTION_CALL_CODE_SECTION_BASE)
    tester.emulator_write_memory(emu_test_defs.FUNCTION_CALL_CODE_SECTION_BASE, func_bytes)
    status, response_data_bytes = tester.client_call_function(transformed_address,
                                                              0x1000,
                                                              0x1500,
                                                              0x2000,
                                                              0x3000)
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value
    assert len(response_data_bytes) == 8
    assert (int.from_bytes(response_data_bytes, 'little') & tester.get_call_return_value_mask())\
        == 0x7500


def test_call_invalid_request_length(tester : et.EmulationTester):
    """
    Test the expected server response when an incorrect request size is provided
    in the request header for calling a function.
    """
    call_request_length = server_defs.ServerCallRequest.sizeof()
    response_header, _ = tester.send_receive_raw_request(server_defs.DEFAULT_MAGIC,
                                                server_defs.ServerOpcode.SERVER_OPCODE_CALL.value,
                                                call_request_length + 1,
                                                data=b'\x00' * (call_request_length + 1))
    assert response_header.status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_initiate_transfer_invalid_request_length(tester : et.EmulationTester):
    """
    Test the expected server response when an incorrect request size is provided
    in the request header for initiating a shellcode transfer.
    """
    initiate_transfer_request_length = server_defs.ServerTransferInitiateRequest.sizeof()
    data_to_send = b'\x01' * (initiate_transfer_request_length + 1)
    initiate_transfer_opcode = server_defs.ServerOpcode.SERVER_OPCODE_TRANSFER_INITIATE.value
    response_header, _ = tester.send_receive_raw_request(server_defs.DEFAULT_MAGIC,
                                                         initiate_transfer_opcode,
                                                         initiate_transfer_request_length + 1,
                                                         data=data_to_send)
    assert response_header.status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_initiate_transfer_zero_size(tester : et.EmulationTester):
    """
    Test the expected server response when a shellcode transfer of 0 bytes is requested.
    """
    status = tester.client_initiate_data_transfer(0)
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_data_transfer_offset_beyond_bounds(tester : et.EmulationTester):
    """
    Test the expected server response when there's an attempt to transfer data
    at an offset which is beyond the end of the declared size for the shellcode.
    """
    shellcode_size = emu_test_defs.SERVER_MAX_DATA_SIZE - 1

    status = tester.client_initiate_data_transfer(shellcode_size)
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status = tester.client_transfer_data(shellcode_size + 1, b"\x00")
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_data_transfer_chunk_overflow(tester : et.EmulationTester):
    """
    Test the expected server response when there's an attempt to write a chunk
    an invalid combination of <offset, chunk_size>, such that it would overflow the
    memory allocated for the shellcode.
    """
    shellcode_size = emu_test_defs.SERVER_MAX_DATA_SIZE - 1

    status = tester.client_initiate_data_transfer(shellcode_size)
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status = tester.client_transfer_data(0, b"\x00" * (shellcode_size + 1))
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_data_transfer_before_initiate(tester : et.EmulationTester):
    """
    Test the expected server response when there's an attempt transfer a shellcode data chunk
    before initiating a data transfer.
    """
    chunk_size = emu_test_defs.SERVER_MAX_DATA_SIZE - server_defs.ServerTransferDataRequest.sizeof()
    status = tester.client_transfer_data(0, b"\x00" * chunk_size)
    assert status == server_defs.ServerStatus.SERVER_INVALID_STATE.value


def test_data_transfer_too_large_size(tester : et.EmulationTester):
    """
    Test the expected server response when there's an attempt to transfer more chunk data
    than a single request supports.
    """
    max_chunk_size = emu_test_defs.SERVER_MAX_DATA_SIZE -\
        server_defs.ServerTransferDataRequest.sizeof()
    shellcode_size = 2 * max_chunk_size
    status = tester.client_initiate_data_transfer(shellcode_size)
    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value

    status = tester.client_transfer_data(0, b"\x00" * (max_chunk_size + 1))
    assert status == server_defs.ServerStatus.SERVER_INVALID_PARAMETER.value


def test_execute_before_initiate(tester : et.EmulationTester):
    """
    Test the expected server response when there's an attempt to execute a shellcode
    before a shellcode transfer was initiated.
    """
    status, _ = tester.client_call_shellcode()
    assert status == server_defs.ServerStatus.SERVER_INVALID_STATE.value


def test_shellcode_execute_sanity(tester : et.EmulationTester):
    """
    Test that executing a shellcode works as expected.
    """
    shellcode_func_bytes = tester.assemble_shellcode_func_asm()
    status, response_data_bytes = tester.client_execute_shellcode_binary(shellcode_func_bytes)

    expected_return_value = 0xAABBCCDDCAFEBABE

    assert status == server_defs.ServerStatus.SERVER_SUCCESS.value
    assert (int.from_bytes(response_data_bytes, 'little') & tester.get_call_return_value_mask())\
    == (expected_return_value & tester.get_call_return_value_mask())
