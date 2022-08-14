
from dataclasses import dataclass
from typing import List

from instance_container_data import InstanceContainerData
from instance_data import DeclarationData
from ports import Port


@dataclass
class FunctionDefinition:
    entity_name: str
    instances: InstanceContainerData
    declarations: List[DeclarationData]
    ports: List[Port]
    def get_memory_port_names(self) -> List[str]:
        return [i.get_name() for i in self.ports if i.is_pointer()]
