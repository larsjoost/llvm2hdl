from abc import ABC, abstractmethod
from typing import List
from instance_data import DeclarationData
from instance_container_data import InstanceContainerData
from source_info import SourceInfoMap

class InstanceContainerInterface(ABC):
    
    @abstractmethod
    def get_instances(self, source_info: SourceInfoMap) -> InstanceContainerData:
        pass

    @abstractmethod
    def get_declarations(self) -> List[DeclarationData]:
        pass

