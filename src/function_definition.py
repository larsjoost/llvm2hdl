
from dataclasses import dataclass
from typing import List

from instance_container_data import InstanceContainerData
from instance_data import DeclarationData
from llvm_function import LlvmFunction
from ports import PortContainer

@dataclass
class FunctionDefinition:
    entity_name: str
    instances: InstanceContainerData
    declarations: List[DeclarationData]
    ports: PortContainer
    function: LlvmFunction
    def get_memory_port_names(self) -> List[str]:
        return self.ports.get_memory_port_names()
