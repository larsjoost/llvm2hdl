from typing import List

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
    previous_tag_name: str

@dataclass
class DeclarationData:
    instance_name: str
    entity_name: str
    type: VhdlDeclarations

