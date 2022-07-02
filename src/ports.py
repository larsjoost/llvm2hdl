
from abc import ABC, abstractmethod

from llvm_declarations import TypeDeclaration

class Port(ABC):
    name: str
    data_type: TypeDeclaration
    def __init__(self, name: str, data_type: TypeDeclaration):
        self.name = name
        self.data_type = data_type
    @abstractmethod
    def is_input(self) -> bool:
        pass

class InputPort(Port):
    def is_input(self) -> bool:
        return True

class OutputPort(Port):
    def is_input(self) -> bool:
        return False
    