from abc import ABC, abstractmethod
from typing import List
from llvmlite.binding import ValueRef
from instance_data import DeclarationData
from instance_container_data import InstanceContainerData

from instance_statistics import InstanceStatistics

class InstanceContainerInterface(ABC):
    
    @abstractmethod
    def resolve_assignment(self, assignment: str) -> List[str]:
        pass

    @abstractmethod
    def get_source(self, operand):
        pass

    @abstractmethod
    def get_assignment(self, instruction : str):
        pass

    @abstractmethod
    def add_instruction(self, instruction: ValueRef, statistics: InstanceStatistics):
        pass

    @abstractmethod
    def get_instances(self) -> InstanceContainerData:
        pass

    @abstractmethod
    def get_declarations(self) -> List[DeclarationData]:
        pass        