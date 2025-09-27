import server_defs
import communication

class ClientInterface:

    def __init__(self, communication_interface : communication.Communication, cmd_callback=None, cmd_callback_arg=None, **configuration):
        self._communication_interface = communication_interface
        self._cmd_callback = cmd_callback
        self._cmd_callback_arg = cmd_callback_arg
        self._process_configuration(**configuration)
        
    
    def _process_configuration(self, **configuration):
        self._magic = server_defs.DEFAULT_MAGIC
        if 'magic' in configuration:
            self._magic = configuration['magic']
        
        self._max_server_data_size = server_defs.DEFAULT_MAX_SERVER_DATA_SIZE
        if 'max_server_data_size' in configuration:
            self._max_server_data_size = configuration['max_server_data_size']
        
        self._shellcode_buffer_size = server_defs.DEFAULT_SHELLCODE_BUFFER_SIZE
        if 'shellcode_buffer_size' in configuration:
            self._shellcode_buffer_size = configuration['shellcode_buffer_size']


    def _build_server_request(self, opcode : int, request_data : bytes) -> bytes:
        request_header = server_defs.ServerRequestHeader.build(dict(magic=self._magic, opcode=opcode, length=len(request_data), subcommand=0, integrity=0))
        return b''.join([request_header, request_data])
    

    def _extract_server_response_data(self):
        response_header_length = server_defs.ServerResponseHeader.sizeof()
        response_header_bytes = self._communication_interface.receive(response_header_length)
        response_header = server_defs.ServerResponseHeader.parse(response_header_bytes)
        status = response_header.status
        response_data_length = response_header.length
        response_data_bytes = self._communication_interface.receive(response_data_length)

        return status, response_data_bytes


    def read_memory(self, address : int, size : int):
        read_request_data = server_defs.ServerReadRequest.build(dict(address=address, size=size))
        read_request = self._build_server_request(server_defs.ServerOpcode.SERVER_OPCODE_READ.value, read_request_data)
        self._communication_interface.send(read_request)
        
        if self._cmd_callback:
            self._cmd_callback(self._cmd_callback_arg)
        return self._extract_server_response_data()


    def write_memory(self, address, data) -> int:
        write_request_data = b''.join([server_defs.ServerWriteRequest.build(dict(address=address)), data])
        write_request = self._build_server_request(server_defs.ServerOpcode.SERVER_OPCODE_WRITE.value, write_request_data)
        self._communication_interface.send(write_request)

        if self._cmd_callback:
            self._cmd_callback(self._cmd_callback_arg)
        status, _ = self._extract_server_response_data()
        return status

    def call_function(self, address, arg1=0, arg2=0, arg3=0, arg4=0):
        call_request_data = server_defs.ServerCallRequest.build(dict(address=address, arg1=arg1, arg2=arg2, arg3=arg3, arg4=arg4))
        call_request = self._build_server_request(server_defs.ServerOpcode.SERVER_OPCODE_CALL.value, call_request_data)
        self._communication_interface.send(call_request)

        if self._cmd_callback:
            self._cmd_callback(self._cmd_callback_arg)
        return self._extract_server_response_data()
