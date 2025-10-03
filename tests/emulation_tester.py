import sys
sys.path.insert(1, '../scripts')

import random
import server_defs
from client_interface import ClientInterface
from test_communication import TestCommunication
import emulation_tester_defs as emu_test_defs


class EmulationTester:
    """
    A utility class implementing the necessary logic to invoke when testing the server
    using an emulator.
    """
    def __init__(self, server_binary_path : str, arch : str):
        if not arch in emu_test_defs.ARCH_TO_ARCH_OBJECT_MAPPING:
            raise ValueError("Invalid architecture specified!")
        
        self._arch_defs = emu_test_defs.ARCH_TO_ARCH_OBJECT_MAPPING[arch]

        with open(server_binary_path, 'rb') as f:
            server_binary = f.read()
        self._initialize_emulator(server_binary)

        test_communication = TestCommunication(self._arch_defs.emu,
                                               emu_test_defs.SERVER_REQUEST_BASE,
                                               emu_test_defs.SERVER_REQUEST_SIZE,
                                               emu_test_defs.SERVER_RESPONSE_BASE,
                                               emu_test_defs.SERVER_RESPONSE_SIZE)
        self._client = ClientInterface(test_communication, self._call_server, self)
     

    def _initialize_emulator(self, server_binary : bytes) -> None:
        """
        Initialize all the necessary emulator memory regions and architecture registers.
        """
        for (base_address, length) in emu_test_defs.MEMORY_MAPPINGS:
            self._arch_defs.emu.mem_map(base_address, length)
        
        self._arch_defs.emu.mem_write(emu_test_defs.CODE_SECTION_BASE, server_binary)
        self._arch_defs.emu.reg_write(self._arch_defs.stack_pointer,
                                      emu_test_defs.STACK_SECTION_BASE + emu_test_defs.STACK_SECTION_LENGTH)
        self._arch_defs.emu.mem_write(emu_test_defs.DATA_SECTION_BASE, 
                                      random.randbytes(emu_test_defs.DATA_SECTION_LENGTH))
    

    def _call_server(self, dummy=None) -> None:
        """
        Invoke a single server execution.
        """
        jump_to_server = self._code_assemble(self._arch_defs.call_server_str,
                                             emu_test_defs.SERVER_CALL_CODE_SECTION_BASE)
        self._arch_defs.emu.mem_write(emu_test_defs.SERVER_CALL_CODE_SECTION_BASE,
                                      jump_to_server)
        self._arch_defs.emu.emu_start(self.transform_address(emu_test_defs.SERVER_CALL_CODE_SECTION_BASE), 
                                      emu_test_defs.SERVER_CALL_CODE_SECTION_BASE + len(jump_to_server))


    def _code_assemble(self, code_str : str, base_address : int = 0) -> bytes:
        """
        Return the binary from of the given assembly code.
        """
        return self._arch_defs.assembler.asm(code_str, base_address, as_bytes=True)[0] 


    def client_read_memory(self, address : int, size : int) -> bytes:
        """
        Read arbitrary memory using the server.
        @param address - the address to read from.
        @param size - the number of bytes to read from the requested address.
        @return the bytes read from the requested address.
        """
        return self._client.read_memory(address, size)


    def client_write_memory(self, address : int, data : bytes) -> int:
        """
        Write arbitrary memory using the server.
        @param address - the address to write to.
        @param data - the bytes to write to the requested address.
        @return the server's status code to the request.
        """
        return self._client.write_memory(address, data)
    

    def client_call_function(self, address : int, arg1 : int = 0, arg2 : int = 0, arg3 : int = 0, arg4 : int = 0):
        """
        Call an arbitrary function using the server.
        @param address - the function's address.
        @param arg1 - arg4 - up to 4 parameters to be given to the function.
        @return a tuple representing the server's status code and the returned value.
        """
        return self._client.call_function(address, arg1, arg2, arg3, arg4)
    

    def client_initiate_data_transfer(self, shellcode_size : int) -> int:
        """
        Inititate a shellcode binary transfer through the server.
        @param shellcode_size - the total size, in bytes, of the shellcode to transfer.
        @return the server's status code to the request.
        """
        return self._client.initiate_data_transfer(shellcode_size)
    

    def client_transfer_data(self, offset : int, data : bytes) -> int:
        """
        Transfer a single chunk of shellcode binary.
        @param offset - the offset, in bytes, to place the chunk at.
        @param data - the chunk's data bytes.
        @return the server's status code to the request.
        """
        return self._client.transfer_data(offset, data)
    

    def client_call_shellcode(self):
        """
        Execute the accumulated shellcode.
        @return a tuple representing the server's status code and the returned value.
        """
        return self._client.call_shellcode()
    

    def client_reset_state(self):
        """
        Reset anything that's not stateless back to its default state.
        @return the server's status code to the request.
        """
        return self._client.reset_state()
    

    def client_execute_shellcode_binary(self, shellcode_binary : bytes):
        """
        Given the entire shellcode binary, execute it in the context of the server.
        @param shellcode_binary - the shellcode's binary data.
        @return
        """
        return self._client.execute_shellcode_binary(shellcode_binary)
    

    def emulator_read_memory(self, address : int, size : int) -> bytes:
        """
        Read memory from the underlying emulator (considered as the ground truth).
        @param address - the address to read from.
        @param size - the number of bytes to read from the requested address.
        @return the bytes read from the requested address.
        """
        return self._arch_defs.emu.mem_read(address, size)


    def emulator_write_memory(self, address : int, data : bytes) -> None:
        """
        Write memory to the underlying emulator (considered as the ground truth).
        @param address - the address to write to.
        @param size - the bytes to write to the requested address.
        """
        self._arch_defs.emu.mem_write(address, data)


    def send_receive_raw_request(self, magic : int, opcode : int, length : int, integrity : int = 0, data : bytes = b''):
        """
        Send a raw request to the server and return the server's response.
        @param magic - the magic to encode within the request.
        @param opcode - the request's operation code.
        @param length - the length, in bytes, of the data portion of the request.
        @param integrity - this parameter is ignored.
        @param data - the data portion of the request.
        """
        request_header = server_defs.ServerRequestHeader.build(dict(magic=magic, opcode=opcode, length=length, subcommand=0, integrity=integrity))
        total_data = b''.join([request_header, data])
        raw_response = self._client.send_receive_raw(total_data)
        raw_response_header = server_defs.ServerResponseHeader.parse(raw_response)
        raw_response_header_length = server_defs.ServerResponseHeader.sizeof()

        return raw_response_header, raw_response[raw_response_header_length : ]


    def assemble_call_func_asm(self) -> bytes:
        """
        Fetch the binary form of the function to be called when testing the function call feature.
        @return the data bytes of the function to be called.
        """
        return self._code_assemble(self._arch_defs.add_4_params_function_str)
    

    def assemble_shellcode_func_asm(self) -> bytes:
        """
        Fetch the binary form of the shellcode to be executed when testing the shellcode execution feature.
        @return the data bytes of the shellcode to be executed.
        """
        return self._code_assemble(self._arch_defs.test_shellcode_str)


    def get_call_return_value_mask(self) -> int:
        """
        Fetch the mask value for the return value of both shellcode execution and arbitrary function calling.
        This value depends on the target architecture.
        @return the mask value for the return value of functions.
        """
        return self._arch_defs.call_return_value_mask
    
    
    def transform_address(self, address : int) -> int:
        """
        Convert an address to an address appropriate for execution before starting executing code
        for that address. Currently, this function is only applicable to ARM code running in Thumb mode,
        which requires the LSB bit of the address to be on before starting execution from that address.
        @return the transformed address.
        """
        if not self._arch_defs.address_transform_func is None:
            return self._arch_defs.address_transform_func(address)
        return address
    