from dataclasses import dataclass
from typing import List

from instance_container_data import InstanceContainerData
from vhdl_instance_data import VhdlInstanceData, VhdlInstanceDataFactory

@dataclass
class VhdlInstanceContainerData:
    instances: List[VhdlInstanceData]
    
    def get_return_instruction_driver(self) -> str:
        return self.instances[-1].instance_name

    def _flatten(self, xss: List[List[str]]) -> List[str]:
        return [x for xs in xss for x in xs]

    def get_memory_instance_names(self) -> List[str]:
        return self._flatten([instance.get_memory_instance_names() for instance in self.instances])

    def get_memory_names(self) -> List[str]:
        return [instance.instance_name for instance in self.instances if instance.is_memory()]
        

class VhdlInstanceContainerDataFactory:

    def get(self, instance_container: InstanceContainerData) -> VhdlInstanceContainerData:
        instances = [VhdlInstanceDataFactory().get(i) for i in instance_container.instances]
        return VhdlInstanceContainerData(instances=instances)
