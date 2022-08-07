
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Union

from llvm_declarations import LlvmName, LlvmType, TypeDeclaration
from source_info import SourceInfo

@dataclass
class PortBase:
    name: LlvmType
    data_type: TypeDeclaration
    
class Port(ABC, PortBase):
    @abstractmethod
    def is_input(self) -> bool:
        pass
    def get_data_width(self) -> str:
        return self.data_type.get_data_width()
    def is_pointer(self) -> bool:
        return self.data_type.is_pointer()
    def get_source_info(self) -> SourceInfo:
        return SourceInfo(destination=self.name,
        output_signal_name=self.name,
        data_type=self.data_type)
    def get_name(self) -> str:
        return self.name.get_name()
    def is_void(self) -> bool:
        return self.data_type.is_void()

class InputPort(Port):
    def is_input(self) -> bool:
        return True

@dataclass
class OutputPort(Port):
    def is_input(self) -> bool:
        return False

@dataclass
class MemoryOutputPort(OutputPort):
    def is_pointer(self) -> bool:
        return True
