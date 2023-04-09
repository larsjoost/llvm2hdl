
from dataclasses import dataclass
from typing import List
from instance_container import InstanceContainer

from llvm_function import LlvmFunction

@dataclass
class FunctionDefinition:
    function: LlvmFunction
    instance_container: InstanceContainer

    def get_memory_port_names(self) -> List[str]:
        return self.function.get_ports().get_memory_port_names()

    def get_entity_name(self) -> str:
        return self.function.name

