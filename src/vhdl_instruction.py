
from dataclasses import dataclass
from typing import List, Optional
from instruction_argument import InstructionArgument, InstructionArgumentContainer

from llvm_instruction import LlvmInstructionInterface
from llvm_port import LlvmOutputPort
from llvm_type_declaration import TypeDeclaration
from memory_interface import MemoryInterface
from vhdl_code_generator import VhdlCodeGenerator


@dataclass
class VhdlInstruction:
    instruction: LlvmInstructionInterface

    def is_work_library(self) -> bool:
        return self.get_library() == "work"

    def get_name(self) -> str:
        instance_name = self.instruction.get_instance_name()
        assert instance_name is not None, f"Instruction {self.instruction} has no instance name"
        return VhdlCodeGenerator().get_vhdl_name(instance_name)

    def get_destination_variable_name(self) -> Optional[str]:
        destination = self.instruction.get_destination()
        return None if destination is None else VhdlCodeGenerator().get_destination_variable_name(name=destination)

    def get_library(self) -> str:
        library = self.instruction.get_library()
        return "work" if library is None else library

    def is_valid(self) -> bool:
        return self.instruction.is_valid()

    def get_source_line(self) -> str:
        return self.instruction.get_source_line()
    
    def get_data_type(self) -> Optional[TypeDeclaration]:
        return self.instruction.get_data_type()

    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return self.instruction.get_memory_interface()

    def map_memory_interface(self) -> bool:
        return self.instruction.map_function_arguments()

    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return self.instruction.get_output_port()

    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        return self.instruction.get_operands()

    def get_generic_map(self) -> Optional[List[str]]:
        return self.instruction.get_generic_map()

    def access_register(self, external_pointer_names: List[str]) -> bool:
        return False

    def _get_variable_declaration(self, operand: InstructionArgument) -> str:
        return VhdlCodeGenerator().get_variable_declaration(name=operand.get_name(), data_width=operand.get_data_width())
        
    def get_variable_declarations(self) -> List[str]:
        operands = self.get_operands()
        assert operands is not None
        return [self._get_variable_declaration(operand=i) for i in operands.arguments]

    def is_return_instruction(self) -> bool:
        return self.instruction.is_return_instruction()

@dataclass
class VhdlInstructionContainer:
    instructions: List[VhdlInstruction]
