from dataclasses import dataclass
from typing import List, Optional

from instruction_interface import InstructionArgument, InstructionGeneral, InstructionInterface
from memory_interface import MemoryInterface, MemoryInterfaceMaster, MemoryInterfaceSlave
from language_generator import LanguageGenerator, LanguageGeneratorInstanceData
from llvm_port import LlvmMemoryOutputPort, LlvmOutputPort
from llvm_declarations import LlvmIntegerDeclaration
from llvm_source_file import LlvmSourceLine
from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmInteger, LlvmVariableName

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
    def generate_code(self, generator: LanguageGenerator) -> None:
        generator.return_operation(data_type=self.data_type, operands=self.operands)
    
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
    def generate_code(self, generator: LanguageGenerator) -> None:
        pass

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
    def generate_code(self, generator: LanguageGenerator) -> None:
        generator.write_signal_declaration(name=self.output_port_name, data_type=self.data_type)
    
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
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.operands + [
            InstructionArgument(signal_name=LlvmInteger(value=self.offset), 
                                data_type=LlvmIntegerDeclaration(data_width=32))]
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmMemoryOutputPort(data_type=self.data_type)
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def generate_code(self, generator: LanguageGenerator) -> None:
        pass
    
@dataclass
class CallInstruction(InstructionInterface):
    opcode: str
    llvm_function: bool
    data_type: TypeDeclaration
    operands: List[InstructionArgument]
    source_line: LlvmSourceLine
    def get_instance_name(self) -> str:
        return self.opcode
    def get_library(self) -> str:
        return "llvm" if self.llvm_function else "work"
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return True
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmOutputPort(data_type=self.data_type, port_name="m_tdata")
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def generate_code(self, generator: LanguageGenerator) -> None:
        data = LanguageGeneratorInstanceData(library=self.get_library(), opcode=self.opcode, data_type=self.data_type, 
                                             operands=self.operands, instance_name=self.opcode, output_port=self.get_output_port(), 
                                             map_memory_interface=True, memory_interface=None, source_line=self.source_line)
        generator.instance(data=data)
    
@dataclass
class LoadInstruction(InstructionInterface):
    opcode: str
    data_type: TypeDeclaration
    output_port_name: Optional[LlvmVariableName]
    operands: List[InstructionArgument]
    source_line: LlvmSourceLine
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmOutputPort(data_type=self.data_type, port_name="m_tdata")
    def get_memory_interface(self) -> Optional[MemoryInterface]:    
        return MemoryInterfaceMaster()
    def generate_code(self, generator: LanguageGenerator) -> None:
        data = LanguageGeneratorInstanceData(library=self.get_library(), opcode=self.opcode, data_type=self.data_type, 
                                             operands=self.operands, instance_name=self.opcode, output_port=self.get_output_port(), 
                                             map_memory_interface=False, memory_interface=None, source_line=self.source_line)
        generator.instance(data=data)

@dataclass
class DefaultInstruction(InstructionInterface):
    opcode: str
    sub_type: Optional[str]
    data_type: TypeDeclaration
    operands: List[InstructionArgument]
    output_port_name: str
    source_line: LlvmSourceLine
    def get_instance_name(self) -> str:
        return InstructionGeneral().get_instance_name(opcode=self.opcode, 
                                                      sub_type=self.sub_type)
    def get_library(self) -> str:
        return InstructionGeneral().get_library()
    def get_data_type(self) -> TypeDeclaration:
        return self.data_type
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.operands
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return True
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return LlvmOutputPort(data_type=self.data_type, port_name=self.output_port_name)
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def generate_code(self, generator: LanguageGenerator) -> None:
        data = LanguageGeneratorInstanceData(library=self.get_library(), opcode=self.opcode, data_type=self.data_type, 
                                             operands=self.operands, instance_name=self.get_instance_name(), output_port=self.get_output_port(), 
                                             map_memory_interface=False, memory_interface=None, source_line=self.source_line)
        generator.instance(data=data)
