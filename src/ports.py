
from abc import ABC, abstractmethod
from typing import Union

from llvm_declarations import LlvmName, TypeDeclaration

class Port(ABC):
    name: Union[LlvmName, str]
    data_type: TypeDeclaration
    def __init__(self, name: str, data_type: TypeDeclaration):
        self.name = name
        self.data_type = data_type
    @abstractmethod
    def is_input(self) -> bool:
        pass
    def get_data_width(self) -> str:
        return self.data_type.get_data_width()
    def get_name(self) -> str:
        if isinstance(self.name, str):
            return self.name
        return self.name.get_name()

class InputPort(Port):
    def is_input(self) -> bool:
        return True

class OutputPort(Port):
    def is_input(self) -> bool:
        return False
    