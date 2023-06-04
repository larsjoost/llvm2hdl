
from abc import ABC, abstractmethod
from typing import List, Optional

from instruction_argument import InstructionArgumentContainer
from llvm_port import LlvmOutputPort
from llvm_type_declaration import TypeDeclaration
from memory_interface import MemoryInterface

class InstructionGeneral:
    def get_instance_name(self, opcode: str, sub_type: Optional[str] = None) -> str:
        name = f"llvm_{opcode}"
        if sub_type is not None:
            name = f"{name}_{sub_type}"
        return name
    def get_library(self) -> str:
        return "llvm"

class InstructionInterface(ABC):
    @abstractmethod
    def get_instance_name(self) -> str:
        pass
    @abstractmethod
    def get_library(self) -> str:
        pass
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
    