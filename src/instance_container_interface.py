from abc import ABC, abstractmethod
from typing import List
from assignment_resolution import AssignmentItem
from instance_data import DeclarationData
from instance_container_data import InstanceContainerData
from instance_statistics import InstanceStatistics
from llvm_declarations import LlvmName, LlvmType
from src.llvm_parser import LlvmInstruction

class InstanceContainerInterface(ABC):
    
    @abstractmethod
    def get_source(self, search_source: LlvmType) -> List[AssignmentItem]:
        pass

    @abstractmethod
    def get_assignment(self, instruction : str):
        pass

    @abstractmethod
    def add_instruction(self, instruction: LlvmInstruction, statistics: InstanceStatistics):
        pass

    @abstractmethod
    def get_instances(self) -> InstanceContainerData:
        pass

    @abstractmethod
    def get_declarations(self) -> List[DeclarationData]:
        pass        