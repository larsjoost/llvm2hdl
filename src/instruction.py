from dataclasses import dataclass
from typing import List, Optional

from instruction_interface import InstructionArgument, InstructionGeneral, InstructionInterface, LlvmMemoryOutputPort, LlvmOutputPort, MemoryInterface, MemoryInterfaceSlave
from llvm_declarations import TypeDeclaration, LlvmName

@dataclass
class ReturnInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    operands: List[InstructionArgument]
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    
@dataclass
class BitcastInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    operands: List[InstructionArgument]
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.operands
    def is_valid(self) -> bool:
        return False
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None

@dataclass
class AllocaInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    output_port_name: Optional[LlvmName]
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_generic_map(self) -> Optional[List[str]]:
        data_width = self.data_type.get_data_width()
        return [f"size => {data_width}/8"]
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return None
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return True
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmMemoryOutputPort(data_type=self.data_type)
    def map_function_arguments(self) -> bool:
        return False
    def get_memory_interface(self) -> MemoryInterface:
        return MemoryInterfaceSlave()
    
@dataclass
class GetelementptrInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    operands: List[InstructionArgument]
    offset: int
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    
@dataclass
class CallInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    operands: List[InstructionArgument]
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return "work"
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return True
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    
@dataclass
class MemoryInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    operands: List[InstructionArgument]
    output_port_name: str
    memory_interface: Optional[MemoryInterface]
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return True
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmMemoryOutputPort(data_type=self.data_type, port_name=self.output_port_name)
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return self.memory_interface
