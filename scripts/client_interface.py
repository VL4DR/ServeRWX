from typing import Tuple
import configuration
import server_defs
import communication


class ClientInterface:
    """
    A class used to provide a reference implementation for communicating with the server.
    """

    def __init__(self,
                 communication_interface : communication.Communication,
                 server_config : configuration.ServerConfig,
                 cmd_callback=None,
                 cmd_callback_arg=None):
        self._communication_interface = communication_interface
        self._server_config_data = server_config.server_config_data
        self._cmd_callback = cmd_callback
        self._cmd_callback_arg = cmd_callback_arg


    def _build_server_request(self, opcode : int, request_data : bytes) -> bytes:
        """
        Given an operation code and the data portion of a request, return the binary form
        of the entire request, filling in the appropriate metadata for the request.
        """
        magic = self._server_config_data.server_magic
        request_header = server_defs.ServerRequestHeader.build({"magic" : magic,
                                                                "opcode" : opcode,
                                                                "length" : len(request_data),
                                                                "subcommand" : 0,
                                                                "integrity" : 0})
        return b''.join([request_header, request_data])


    def _extract_server_response_raw(self) -> bytes:
        """
        Read the entire response data and returns its raw, unparsed form.
        """
        if self._cmd_callback:
            self._cmd_callback(self._cmd_callback_arg)
        response_header_length = server_defs.ServerResponseHeader.sizeof()
        response_header_bytes = self._communication_interface.receive(response_header_length)
        response_header = server_defs.ServerResponseHeader.parse(response_header_bytes)
        response_data_length = response_header.length
        response_data_bytes = self._communication_interface.receive(response_data_length)

        return b''.join([response_header_bytes, response_data_bytes])


    def _extract_server_response_data(self) -> Tuple[int, bytes]:
        """
        Read the entire response data and return the response's status code,
        as well as its data portion.
        """
        response_raw = self._extract_server_response_raw()
        response_header = server_defs.ServerResponseHeader.parse(response_raw)
        response_header_length = server_defs.ServerResponseHeader.sizeof()

        return response_header.status, response_raw[response_header_length : ]


    def send_receive_raw(self, data : bytes) -> bytes:
        """
        Send a raw request (including the header) and return the server's raw response.
        @param data - the raw request (including the header) to send to the server.
        @return the raw response (including the header) from the server.
        """
        self._communication_interface.send(data)

        return self._extract_server_response_raw()


    def read_memory(self, address : int, size : int) -> Tuple[int, bytes]:
        """
        Read arbitrary memory.
        @param address - the address to read from.
        @param size - the number of bytes to read from the requested address.
        @return a tuple representing the status code and the response data for the given request.
        """
        read_request_data = server_defs.ServerReadRequest.build({"address" : address,
                                                                 "size" : size})
        read_request = self._build_server_request(server_defs.ServerOpcode.SERVER_OPCODE_READ.value,
                                                  read_request_data)
        self._communication_interface.send(read_request)

        return self._extract_server_response_data()


    def write_memory(self, address : int, data : bytes) -> int:
        """
        Write arbitrary memory.
        @param address - the address to write to.
        @param data - the data bytes to write ot the requested address.
        @return the server's status code for the given request.
        """
        write_request_data = b''.join([
            server_defs.ServerWriteRequest.build({"address" : address}),
            data])
        write_request = self._build_server_request(
            server_defs.ServerOpcode.SERVER_OPCODE_WRITE.value,
            write_request_data)
        self._communication_interface.send(write_request)

        status, _ = self._extract_server_response_data()
        return status


    def call_function(self,
                      address : int,
                      arg1 : int = 0,
                      arg2 : int = 0,
                      arg3 : int = 0,
                      arg4 : int = 0) -> Tuple[int, bytes]:
        """
        Call an arbitrary function. The called function will be called using the calling convention
        the server uses.
        @param address - the address of the function to be called.
        @param arg1 - arg4 - the parameters to be passed to the called function.
        @return a tuple representing the status code and the value returned from the function.
        """
        call_request_data = server_defs.ServerCallRequest.build({"address" : address,
                                                                 "arg1" : arg1,
                                                                 "arg2" : arg2,
                                                                 "arg3" : arg3,
                                                                 "arg4" : arg4})
        call_request = self._build_server_request(server_defs.ServerOpcode.SERVER_OPCODE_CALL.value,
                                                  call_request_data)
        self._communication_interface.send(call_request)

        return self._extract_server_response_data()


    def initiate_data_transfer(self, shellcode_size : int) -> int:
        """
        Start a shellcode transfer.
        @param shellcode_size - the declared size, in bytes, of the shellcoded to be transferred.
        @return the server's status code for the given request. 
        """
        initiate_data_transfer_data = server_defs.ServerTransferInitiateRequest.build(
            {"shellcode_size" : shellcode_size})
        initiate_data_transfer_request = self._build_server_request(
            server_defs.ServerOpcode.SERVER_OPCODE_TRANSFER_INITIATE.value,
            initiate_data_transfer_data)
        self._communication_interface.send(initiate_data_transfer_request)

        status, _ = self._extract_server_response_data()
        return status


    def transfer_data(self, offset : int, data : bytes) -> int:
        """
        Transfer a single chunk of shellcode data.
        @param offset - the offset, in bytes, to place the chunk at.
        @param data - the chunk's data bytes.
        @return the server's status code for the given request.
        """
        transfer_data_request_data = b''.join([
            server_defs.ServerTransferDataRequest.build({"offset" : offset}),
            data])
        transfer_data_request = self._build_server_request(
            server_defs.ServerOpcode.SERVER_OPCODE_TRANSFER_DATA.value,
            transfer_data_request_data)
        self._communication_interface.send(transfer_data_request)

        status, _ = self._extract_server_response_data()
        return status


    def call_shellcode(self) -> Tuple[int, bytes]:
        """
        Execute the accumulated shellcode.
        @return a tuple representing the status code and the value returned from the shellcode.
        """
        execute_request = self._build_server_request(
            server_defs.ServerOpcode.SERVER_OPCODE_EXECUTE.value,
            b'')
        self._communication_interface.send(execute_request)

        return self._extract_server_response_data()


    def reset_state(self) -> int:
        """
        Reset anything that's not stateless back to its default state.
        @return the server's status code to the request.
        """
        reset_state_request = self._build_server_request(
            server_defs.ServerOpcode.SERVER_OPCODE_RESET_STATE.value,
            b'')
        self._communication_interface.send(reset_state_request)

        status, _ = self._extract_server_response_data()
        return status


    def execute_shellcode_binary(self, shellcode_binary : bytes) -> Tuple[int, bytes]:
        """
        Given the entire shellcode binary, execute it in the context of the server.
        @param shellcode_binary - the shellcode's binary data.
        @return a tuple representing the status code and the value returned from the shellcode.
        """
        shellcode_binary_len = len(shellcode_binary)
        if shellcode_binary_len == 0:
            raise ValueError("Empty shellcode file provided!")

        status = self.initiate_data_transfer(shellcode_binary_len)
        if status != server_defs.ServerStatus.SERVER_SUCCESS.value:
            raise RuntimeError(f"Initiating shellcode transfer failed with error {status}!")

        transfer_data_request_size = server_defs.ServerTransferDataRequest.sizeof()
        chunk_size = self._server_config_data.server_max_data_size - transfer_data_request_size

        for chunk_offset in range(0, shellcode_binary_len, chunk_size):
            chunk_end = min(shellcode_binary_len, chunk_offset + chunk_size)
            current_data_chunk = shellcode_binary[chunk_offset : chunk_end]
            status = self.transfer_data(chunk_offset, current_data_chunk)
            if status != server_defs.ServerStatus.SERVER_SUCCESS.value:
                raise RuntimeError(f"Transferring chunk at offset {chunk_offset}\
                                   failed with status {status}!")

        return self.call_shellcode()

    def execute_shellcode_file(self, shellcode_binary_path : str) -> Tuple[int, bytes]:
        """
        Given a path to a shellcode binary, execute it in the context of the server.
        @param shellcode_binary_path - path to the shellcode binary.
        @return a tuple representing the status code and the value returned from the shellcode.
        """
        with open(shellcode_binary_path, "rb") as f:
            shellcode_binary = f.read()

        return self.execute_shellcode_binary(shellcode_binary)
