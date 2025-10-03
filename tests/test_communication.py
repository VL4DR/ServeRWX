import unicorn as uc
from communication import Communication

class TestCommunication(Communication):
    """
    A class that simulates sending and receiving bytes using an emulator.
    """
    def __init__(self, emu : uc.Uc, tx_base_address : int, tx_buffer_size : int, rx_base_address : int, rx_buffer_size : int):
        super(TestCommunication).__init__()
        self._emu = emu
        self._tx_base_address = tx_base_address
        self._tx_buffer_size = tx_buffer_size
        self._current_tx_ptr = 0
        self._rx_base_address = rx_base_address
        self._rx_buffer_size = rx_buffer_size
        self._current_rx_ptr = 0
    
    
    def send(self, data : bytes) -> None:
        """
        Insert a sequence of bytes to the send buffer.
        @param data - the bytes to insert to the send buffer.
        """
        if self._current_tx_ptr + len(data) > self._tx_buffer_size:
            self._current_tx_ptr = 0

        self._emu.mem_write(self._tx_base_address + self._current_tx_ptr, data)
        self._current_tx_ptr += len(data)
    

    def receive(self, num_bytes : int) -> bytes:
        """
        Read the requested number of bytes from the receive buffer.
        @param num_bytes - number of bytes to read from the receive buffer.
        @return the bytes read.
        """
        if self._current_rx_ptr + num_bytes > self._rx_buffer_size:
            self._current_rx_ptr = 0
        
        receive_data = self._emu.mem_read(self._rx_base_address + self._current_rx_ptr, num_bytes)
        self._current_rx_ptr += num_bytes
        return receive_data
