from typing import List, Optional

from dataclasses import dataclass
from llvm_instruction import LlvmInstructionInterface
from llvm_parser import InstructionArgument, MemoryInterface, LlvmOutputPort
from llvm_type_declaration import TypeDeclaration

@dataclass
class InstanceData:
    instance_name: str
    entity_name: str
    library: str
    output_port: Optional[LlvmOutputPort]
    tag_name: str
    input_ports: List[InstructionArgument]
    memory_interface: Optional[MemoryInterface]
    instruction: LlvmInstructionInterface

@dataclass
class DeclarationData:
    instance_name: str
    declaration_name: str
    data_type: TypeDeclaration

    def is_void(self) -> bool:
        return self.data_type.is_void()

