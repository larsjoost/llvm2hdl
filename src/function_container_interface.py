
from abc import ABC, abstractmethod
from typing import List
from ports import PortContainer

from signal_interface import SignalInterface

class FunctionContainerInterface(ABC):
    
    @abstractmethod
    def add_instance_signals(self, signals: List[str]) -> None:
        pass

    @abstractmethod
    def get_signals(self) -> List[SignalInterface]:
        pass

    @abstractmethod
    def get_ports(self) -> PortContainer:
        pass