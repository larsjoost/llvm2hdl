
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

class InputPort(Port):
    def is_input(self) -> bool:
        return True

class OutputPort(Port):
    def is_input(self) -> bool:
        return False
    