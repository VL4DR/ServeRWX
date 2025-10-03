from abc import ABC, abstractmethod

class Communication(ABC):
    """
    An abstract class that provides the API for communicating with the server.
    """
    def __init__(self):
        pass


    @abstractmethod
    def send(self, data : bytes):
        """
        Send a sequence of bytes to the server.
        @param data - the bytes to send.
        """


    @abstractmethod
    def receive(self, num_bytes : int):
        """
        Receive some bytes from the server.
        @param num_bytes - the number of bytes to receive.
        """
