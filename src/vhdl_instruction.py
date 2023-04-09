
from dataclasses import dataclass
from typing import List, Optional

from llvm_instruction import LlvmInstructionInterface
from llvm_type_declaration import TypeDeclaration
from memory_interface import MemoryInterface


@dataclass
class VhdlInstruction:
    instruction: LlvmInstructionInterface

    def is_work_library(self) -> bool:
        return self.get_library() == "work"

    def get_name(self) -> str:
        instance_name = self.instruction.get_instance_name()
        assert instance_name is not None
        return instance_name

    def get_library(self) -> str:
        library = self.instruction.get_library()
        return "work" if library is None else library

    def get_source_line(self) -> str:
        return self.instruction.get_source_line()
    
    def get_data_type(self) -> Optional[TypeDeclaration]:
        return self.instruction.get_data_type()

    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return self.instruction.get_memory_interface()

    def map_memory_interface(self) -> bool:
        return self.instruction.map_function_arguments()

@dataclass
class VhdlInstructionContainer:
    instructions: List[VhdlInstruction]
