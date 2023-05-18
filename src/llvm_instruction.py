
from abc import ABC
from dataclasses import dataclass
from typing import List, Optional

from instruction_argument import InstructionArgument, InstructionArgumentContainer
from instruction_interface import LlvmOutputPort, MemoryInterface
from llvm_source_file import LlvmSourceLine

from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration
from vhdl_memory import VhdlMemory

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
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    def is_return_instruction(self) -> bool:
        return False
    def get_memory_drivers(self, memory_instance: VhdlMemory) -> List[str]:
        return []

@dataclass
class LlvmInstructionContainer:
    instructions: List[LlvmInstructionInterface]

    def get_external_pointer_names(self) -> List[str]:
        external_pointer_names: List[str] = []
        for instruction in self.instructions:
            external_pointer_names.extend(instruction.get_external_pointer_names())
        return external_pointer_names
    
    def get_memory_port_name(self, instruction: LlvmInstructionInterface, port: InstructionArgument) -> Optional[str]:
        if not port.is_pointer():
            return None
        if not instruction.map_function_arguments():
            return None
        memory_interface_name = instruction.get_instance_name()
        return f"{memory_interface_name}_{port.get_name()}"

    def _get_instance_name(self, instruction: LlvmInstructionInterface) -> str:
        instance_name = instruction.get_instance_name()
        assert instance_name is not None
        return instance_name

    def _get_operands_memory_instance_names(self, instruction: LlvmInstructionInterface) -> List[str]:
        operands = instruction.get_operands()
        if operands is None:
            return []
        result = [self.get_memory_port_name(instruction=instruction, port=i) for i in operands.arguments]
        return [i for i in result if i is not None]

    def _get_memory_instance_names(self, instruction: LlvmInstructionInterface) -> List[str]:
        memory_interface = instruction.get_memory_interface()
        if memory_interface is not None and memory_interface.is_master():
            return [self._get_instance_name(instruction=instruction)]
        return self._get_operands_memory_instance_names(instruction=instruction)
    
    def get_memory_instance_names(self) -> List[str]:
        memory_instance_names: List[str] = []
        for instruction in self.instructions:
            memory_instance_names.extend(self._get_memory_instance_names(instruction=instruction))
        return memory_instance_names
    
    def get_memory_names(self) -> List[str]:        
        return [self._get_instance_name(instruction=instruction) for instruction in self.instructions if instruction.is_memory()]

    def get_memory_drivers(self, memory_instance: VhdlMemory) -> List[str]:
        memory_drivers = []
        for instruction in self.instructions:
            memory_drivers.extend(instruction.get_memory_drivers(memory_instance=memory_instance))
        return memory_drivers