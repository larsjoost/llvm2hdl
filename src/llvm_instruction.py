
from abc import ABC
from dataclasses import dataclass
from typing import List, Optional

from instruction_argument import InstructionArgumentContainer
from instruction_interface import LlvmOutputPort, MemoryInterface
from llvm_source_file import LlvmSourceLine

from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration

@dataclass
class LlvmInstructionData:
    source_line: LlvmSourceLine
    
class LlvmInstructionInterface(ABC, LlvmInstructionData):
    def get_destination(self) -> Optional[LlvmVariableName]:
        return None
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        return None
    def get_data_type(self) -> Optional[TypeDeclaration]:
        return None
    def get_library(self) -> Optional[str]:
        return None
    def get_instance_name(self) -> Optional[str]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False
    def get_source_line(self) -> str:
        return self.source_line.get_elaborated()        
    def get_external_pointer_names(self) -> List[str]:
        return []

@dataclass
class LlvmInstructionContainer:
    instructions: List[LlvmInstructionInterface]

    def get_external_pointer_names(self) -> List[str]:
        external_pointer_names: List[str] = []
        for instruction in self.instructions:
            external_pointer_names.extend(instruction.get_external_pointer_names())
        return external_pointer_names