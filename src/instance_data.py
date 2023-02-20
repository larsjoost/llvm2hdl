from typing import Any, List, Optional

from dataclasses import dataclass
from llvm_instruction import LlvmInstruction
from llvm_parser import InstructionArgument, MemoryInterface, LlvmOutputPort
from llvm_type_declaration import TypeDeclaration

@dataclass
class InstanceData:
    instance_name: str
    entity_name: str
    library: str
    output_port: Optional[LlvmOutputPort]
    tag_name: str
    generic_map: Optional[List[str]]
    input_ports: List[InstructionArgument]
    previous_instance_name: Optional[str]
    memory_interface: Optional[MemoryInterface]
    instruction: LlvmInstruction

@dataclass
class DeclarationData:
    instance_name: str
    declaration_name: str
    data_type: TypeDeclaration

    def is_void(self) -> bool:
        return self.data_type.is_void()

