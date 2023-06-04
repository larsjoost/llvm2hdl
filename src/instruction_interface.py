
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from instruction_argument import InstructionArgumentContainer
from llvm_port import LlvmOutputPort
from llvm_type import LlvmInstanceName
from llvm_type_declaration import TypeDeclaration
from memory_interface import MemoryInterface

@dataclass
class InstructionInterface(ABC):
    opcode: LlvmInstanceName
    def get_instance_name(self) -> str:
        return self.opcode.get_instance_name()
    def get_library(self) -> str:
        return self.opcode.get_library()
    @abstractmethod
    def get_data_type(self) -> TypeDeclaration:
        pass
    @abstractmethod
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        pass
    @abstractmethod
    def is_valid(self) -> bool:
        pass
    @abstractmethod
    def access_memory_contents(self) -> bool:
        pass
    @abstractmethod
    def map_function_arguments(self) -> bool:
        pass
    @abstractmethod
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        pass
    @abstractmethod
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        pass
    @abstractmethod
    def get_external_pointer_names(self) -> List[str]:
        pass
    def is_return_instruction(self) -> bool:
        return False
    def returns_pointer(self) -> bool:
        return False
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    