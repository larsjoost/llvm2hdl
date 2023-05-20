from dataclasses import dataclass
from typing import List, Optional
from instruction_argument import InstructionArgumentContainer, InstructionArgument

from instruction_interface import InstructionGeneral, InstructionInterface
from memory_interface import MemoryInterface, MemoryInterfaceMaster, MemoryInterfaceSlave
from llvm_port import LlvmMemoryOutputPort, LlvmOutputPort
from llvm_declarations import LlvmIntegerDeclaration
from llvm_source_file import LlvmSourceLine
from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmInteger, LlvmVariableName

@dataclass
class ReturnInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    operands: InstructionArgumentContainer
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def access_memory_contents(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def get_external_pointer_names(self) -> List[str]:
        return []
    def is_return_instruction(self) -> bool:
        return True
    
@dataclass
class BitcastInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    operands: InstructionArgumentContainer
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        return self.operands
    def is_valid(self) -> bool:
        return False
    def access_memory_contents(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def get_external_pointer_names(self) -> List[str]:
        return []

@dataclass
class AllocaInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    output_port_name: Optional[LlvmVariableName]
    initialization: Optional[List[str]]
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    # TODO: Delete this
    def get_generic_map(self) -> Optional[List[str]]:
        data_width = self.data_type.get_data_width()
        generic_map = [f"size_bytes => ({data_width})/8"]
        if self.initialization is not None:
            initialization = ", ".join(self.initialization)
            generic_map.append(f"initialization => ({initialization})")
        return generic_map
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        return None
    def is_valid(self) -> bool:
        return True
    def access_memory_contents(self) -> bool:
        return True
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmMemoryOutputPort(data_type=self.data_type)
    def map_function_arguments(self) -> bool:
        return False
    def get_memory_interface(self) -> MemoryInterface:
        return MemoryInterfaceSlave()
    def get_external_pointer_names(self) -> List[str]:
        return []

@dataclass
class GetelementptrInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    operands: InstructionArgumentContainer
    offset: int
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        arguments = self.operands.arguments + [
            InstructionArgument(signal_name=LlvmInteger(value=self.offset), 
                                data_type=LlvmIntegerDeclaration(data_width=32))]
        return InstructionArgumentContainer(arguments=arguments)
    def is_valid(self) -> bool:
        return True
    def access_memory_contents(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmMemoryOutputPort(data_type=self.data_type)
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def get_external_pointer_names(self) -> List[str]:
        return []
    
@dataclass
class CallInstruction(InstructionInterface):
    opcode: str
    llvm_function: bool
    data_type: TypeDeclaration
    operands: InstructionArgumentContainer
    source_line: LlvmSourceLine
    def get_instance_name(self) -> str:
        return self.opcode
    def get_library(self) -> str:
        return "llvm" if self.llvm_function else "work"
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def access_memory_contents(self) -> bool:
        return True
    def map_function_arguments(self) -> bool:
        return True
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmOutputPort(data_type=self.data_type, port_name="m_tdata")
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def get_external_pointer_names(self) -> List[str]:
        return self.operands.get_pointer_names()

@dataclass
class LoadInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    output_port_name: Optional[LlvmVariableName]
    operands: InstructionArgumentContainer
    source_line: LlvmSourceLine
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def access_memory_contents(self) -> bool:
        return True
    def map_function_arguments(self) -> bool:
        return False
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmOutputPort(data_type=self.data_type, port_name="m_tdata")
    def get_memory_interface(self) -> Optional[MemoryInterface]:    
        return MemoryInterfaceMaster()
    def get_external_pointer_names(self) -> List[str]:
        return []

@dataclass
class DefaultInstruction(InstructionInterface):
    opcode: str
    sub_type: Optional[str]
    data_type: TypeDeclaration
    operands: InstructionArgumentContainer
    output_port_name: str
    source_line: LlvmSourceLine
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode, 
                                                      sub_type=self.sub_type)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def access_memory_contents(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return True
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmOutputPort(data_type=self.data_type, port_name=self.output_port_name)
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def get_external_pointer_names(self) -> List[str]:
        return []
