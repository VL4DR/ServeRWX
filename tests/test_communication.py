import sys
sys.path.insert(1, '../scripts')

from communication import Communication

class TestCommunication(Communication):
    def __init__(self, emu, tx_base_address, tx_buffer_size, rx_base_address, rx_buffer_size):
        super().__init__()
        self._emu = emu
        self._tx_base_address = tx_base_address
        self._tx_buffer_size = tx_buffer_size
        self._current_tx_ptr = 0
        self._rx_base_address = rx_base_address
        self._rx_buffer_size = rx_buffer_size
        self._current_rx_ptr = 0
    
    
    def send(self, data : bytes):
        if self._current_tx_ptr + len(data) > self._tx_buffer_size:
            self._current_tx_ptr = 0

        self._emu.mem_write(self._tx_base_address + self._current_tx_ptr, data)
        self._current_tx_ptr += len(data)
    

    def receive(self, num_bytes : int) -> bytes:
        if self._current_rx_ptr + num_bytes > self._rx_buffer_size:
            self._current_rx_ptr = 0
        
        receive_data = self._emu.mem_read(self._rx_base_address + self._current_rx_ptr, num_bytes)
        self._current_rx_ptr += num_bytes
        return receive_data
