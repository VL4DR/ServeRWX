from abc import ABC, abstractmethod

class Communication(ABC):
    def __init__():
        pass
    
    
    @abstractmethod
    def send(self, data : bytes):
        pass

    
    @abstractmethod
    def receive(self, num_bytes : int):
        pass
    