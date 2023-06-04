from dataclasses import dataclass
from typing import List, Optional
from instruction_argument import InstructionArgumentContainer

from instruction_interface import InstructionGeneral, InstructionInterface
from llvm_declarations import LlvmDeclarationFactory
from llvm_destination import LlvmDestination
from llvm_intruction_parser import LlvmInstructionParserArguments, LlvmInstructionParserInterface
from llvm_source_file import LlvmSourceLine
from memory_interface import MemoryInterface
from llvm_port import LlvmMemoryOutputPort, LlvmOutputPort
from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmVariableName

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
        return LlvmMemoryOutputPort(data_type=self.data_type, port_name=self.output_port_name)
    def map_function_arguments(self) -> bool:
        return False
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def get_external_pointer_names(self) -> List[str]:
        return []

class AllocaInstructionParser(LlvmInstructionParserInterface):

    def parse(self, arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> InstructionInterface:
        # alloca [3 x i32], align 4
        # alloca i32, align 4
        # alloca %class.ClassTest, align 4
        x = arguments.instruction.split(",")
        y = x[0].split(maxsplit=1)
        opcode = y[0]
        data_type_position = y[1].replace("[", "").replace("]", "")
        data_type = LlvmDeclarationFactory().get(data_type=data_type_position, constants=arguments.constants)
        initialization = arguments.constants.get_initialization(name=arguments.destination.name)
        return AllocaInstruction(
            opcode=opcode, data_type=data_type, output_port_name=arguments.destination.name, initialization=initialization
        )

    def match(self, instruction: List[str]) -> bool:
        return instruction[0] == "alloca"
