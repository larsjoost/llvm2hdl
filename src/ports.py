
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmType
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
        return self.name.translate_name()
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


class PortGenerator(ABC):
    @abstractmethod
    def get_ports(self, port: Port) -> List[str]:
        pass
    @abstractmethod
    def get_data_width(self, port: Port) -> str:
        pass

@dataclass
class PortContainer:
    ports: List[Port]
    def __init__(self, ports: Optional[List[Port]] = None) -> None:
        self.ports = [] if ports is None else ports
    def get_memory_port_names(self) -> List[str]:
        return [i.get_name() for i in self.ports if i.is_pointer()]
    def get_ports(self, generator: PortGenerator) -> List[str]:
        x = []
        for i in self.ports:
            x.extend(generator.get_ports(port=i))
        return x
    def get_total_input_data_width(self, generator: PortGenerator) -> List[str]:
        return [generator.get_data_width(port=i) for i in self.ports if i.is_input()]
