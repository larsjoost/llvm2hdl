from typing import List, Optional

from dataclasses import dataclass
from llvm_parser import InstructionArgument, OutputPort
from vhdl_declarations import VhdlDeclarations

@dataclass
class InstanceData:
    instance_name: str
    entity_name: str
    library: str
    output_port: OutputPort
    tag_name: str
    input_ports: List[InstructionArgument]
    previous_instance_name: Optional[str]
    def _get_signal_name(self, instance_name: str, signal_name: str) -> str:
        return instance_name + "_" + signal_name + "_i"
    def get_previous_instance_signal_name(self, signal_name: str) -> Optional[str]:
        if self.previous_instance_name is None:
            return None
        return self._get_signal_name(instance_name=self.previous_instance_name, signal_name=signal_name)
    def get_own_instance_signal_name(self, signal_name) -> str:
        return self._get_signal_name(instance_name=self.instance_name, signal_name=signal_name)


@dataclass
class DeclarationData:
    instance_name: str
    entity_name: str
    type: VhdlDeclarations

