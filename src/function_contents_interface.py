
from abc import ABC, abstractmethod


class FunctionContentsInterface(ABC):
    
    @abstractmethod
    def append_instance(self, name: str) -> None:
        pass

    @abstractmethod
    def write_body(self, *args, **kwargs) -> None:
        pass