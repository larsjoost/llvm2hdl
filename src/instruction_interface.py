
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional, Union

from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmVariableName, LlvmType
from vhdl_declarations import VhdlDeclarations

@dataclass
class LlvmOutputPort:
    data_type : TypeDeclaration
    port_name: Optional[Union[LlvmVariableName, str]] = None
    def get_type_declarations(self) -> str:
        return VhdlDeclarations(self.data_type).get_type_declarations()
    def is_pointer(self) -> bool:
        return False
    def get_name(self) -> Optional[str]:
        if isinstance(self.port_name, LlvmVariableName):
            return self.port_name.get_name()
        return self.port_name
    def is_void(self) -> bool:
        return self.data_type.is_void()

@dataclass
class LlvmMemoryOutputPort(LlvmOutputPort):
    def is_pointer(self) -> bool:
        return True

class MemoryInterface(ABC):
    def is_master(self) -> bool:
        return False

class MemoryInterfaceMaster(MemoryInterface):
    def is_master(self) -> bool:
        return True

class MemoryInterfaceSlave(MemoryInterface):
    pass

@dataclass
class InstructionArgument:
    signal_name: LlvmType
    data_type : TypeDeclaration
    unnamed : bool = False 
    port_name: Optional[str] = None
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.data_type.get_dimensions()
    def single_dimension(self) -> bool:
        return self.data_type.single_dimension()
    def is_pointer(self) -> bool:
        return self.data_type.is_pointer()
    def get_array_index(self) -> Optional[str]:
        return self.data_type.get_array_index()
    def get_name(self) -> str:
        return self.signal_name.get_name()
    def get_value(self) -> str:
        return self.signal_name.get_value()
    def get_data_width(self) -> str:
        return self.data_type.get_data_width()
    def is_integer(self) -> bool:
        if isinstance(self.signal_name, LlvmType):
            return self.signal_name.is_integer()
        return False

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

