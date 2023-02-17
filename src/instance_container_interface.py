from abc import ABC, abstractmethod
from typing import List, Optional
from instance_data import DeclarationData
from instance_container_data import InstanceContainerData
from llvm_type import LlvmType
from source_info import SourceInfo

class InstanceContainerInterface(ABC):
    
    @abstractmethod
    def get_source(self, search_source: LlvmType) -> Optional[SourceInfo]:
        pass

    @abstractmethod
    def get_instances(self) -> InstanceContainerData:
        pass

    @abstractmethod
    def get_declarations(self) -> List[DeclarationData]:
        pass

