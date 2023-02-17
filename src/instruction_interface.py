
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Union
from instruction_argument import InstructionArgument
from llvm_port import LlvmOutputPort

from llvm_type_declaration import TypeDeclaration

class MemoryInterface(ABC):
    def is_master(self) -> bool:
        return False

class MemoryInterfaceMaster(MemoryInterface):
    def is_master(self) -> bool:
        return True

class MemoryInterfaceSlave(MemoryInterface):
    pass

class InstructionGeneral:
    def get_instance_name(self, opcode: str) -> str:
        return f"llvm_{opcode}"
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
    def get_generic_map(self) -> Optional[List[str]]:
        pass
    @abstractmethod
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        pass
    @abstractmethod
    def is_valid(self) -> bool:
        pass
    @abstractmethod
    def is_memory(self) -> bool:
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

