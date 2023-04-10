
from abc import ABC, abstractmethod
from typing import List

from llvm_type_declaration import TypeDeclaration
from ports import PortContainer
from signal_interface import SignalInterface

class FunctionContentsInterface(ABC):
    
    @abstractmethod
    def append_instance(self, name: str) -> None:
        pass

    @abstractmethod
    def write_tag_declaration(self, signal_name: str, instance_name: str, destination: str, data_type: TypeDeclaration) -> None:
        pass

    @abstractmethod
    def write_body(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def add_signal(self, signal: SignalInterface) -> None:
        pass

    @abstractmethod
    def add_instance_signals(self, signals: List[str]) -> None:
        pass

    @abstractmethod
    def get_signals(self) -> List[SignalInterface]:
        pass

    @abstractmethod
    def get_ports(self) -> PortContainer:
        pass

