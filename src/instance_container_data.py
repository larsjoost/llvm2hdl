from dataclasses import dataclass
from typing import List

from instance_data import InstanceData

@dataclass
class InstanceContainerData:
    instances: List[InstanceData]
    
    def get_return_instruction_driver(self) -> str:
        return self.instances[-1].instance_name

    def get_memory_instance_names(self) -> List[str]:
        return [instance.instance_name for instance in self.instances if instance.memory_interface is not None]

    def get_memory_names(self) -> List[str]:
        return [instance.instance_name for instance in self.instances if instance.is_memory()]