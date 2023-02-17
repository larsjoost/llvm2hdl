
from abc import ABC
from dataclasses import dataclass
from typing import List, Optional
from instruction_argument import InstructionArgument
from instruction_interface import LlvmOutputPort, MemoryInterface

from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration


@dataclass
class LlvmInstruction(ABC):
    def get_destination(self) -> Optional[LlvmVariableName]:
        return None
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return None
    def get_data_type(self) -> Optional[TypeDeclaration]:
        return None
    def get_library(self) -> Optional[str]:
        return None
    def get_instance_name(self) -> Optional[str]:
        return None
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False

