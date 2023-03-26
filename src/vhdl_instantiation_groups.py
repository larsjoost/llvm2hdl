
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from vhdl_instance_data import VhdlInstanceData

class VhdlInstantiationGroupBase(ABC):
    @abstractmethod
    def append(self, instance: VhdlInstanceData) -> bool:
        pass

@dataclass
class VhdlRegisterAccessGroup(VhdlInstantiationGroupBase):
    instances: List[VhdlInstanceData]
    def append(self, instance: VhdlInstanceData) -> bool:
        if not instance.access_register():
            return False
        self.instances.append(instance)
        return True

@dataclass    
class VhdlInstanceGroup(VhdlInstantiationGroupBase):
    instance: VhdlInstanceData
    def append(self, instance: VhdlInstanceData) -> bool:
        return False

class VhdlInstantiationGroupsGenerator:

    def _add_group(self, groups: List[VhdlInstantiationGroupBase], instance: VhdlInstanceData) -> None:
        if instance.access_register():
            groups.append(VhdlRegisterAccessGroup(instances=[instance]))
        else:
            groups.append(VhdlInstanceGroup(instance=instance))

    def get_groups(self, instances: List[VhdlInstanceData]) -> List[VhdlInstantiationGroupBase]:
        groups: List[VhdlInstantiationGroupBase] = []
        for i in instances:
            appended_to_group = groups[-1].append(instance=i) if groups else False
            if not appended_to_group:
                self._add_group(groups=groups, instance=i)
        return groups
 