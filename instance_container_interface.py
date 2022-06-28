from abc import ABC, abstractmethod
from typing import List
from llvmlite.binding import ValueRef
from file_writer import FileWriter

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
    def write_instances(self, file_handle: FileWriter):
        pass

    @abstractmethod
    def write_declarations(self, file_handle: FileWriter):
        pass        