

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from function_container_interface import FunctionContainerInterface
from function_contents_interface import FunctionContentsInterface
from instruction_argument import InstructionArgument
from memory_interface import MemoryInterface
from llvm_globals_container import GlobalsContainer
from llvm_port import LlvmOutputPort
from llvm_source_file import LlvmSourceLine
from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration

@dataclass    
class LanguageGeneratorInstanceData:
    library: str
    opcode: str
    data_type: TypeDeclaration
    operands: List[InstructionArgument]
    instance_name: str
    output_port: Optional[LlvmOutputPort]
    map_memory_interface: bool
    memory_interface: Optional[MemoryInterface]
    source_line: LlvmSourceLine
    generic_map: Optional[List[str]] = None

@dataclass
class LanguageGeneratorCallData:
    opcode: str
    data_type: TypeDeclaration
    operands: List[InstructionArgument]
    source_line: LlvmSourceLine

    def _get_variable_name(self, name: str) -> str:
        return f"{name}_v"

    def _get_variable_declaration(self, operand: InstructionArgument) -> str:
        variable_name = self._get_variable_name(operand.get_name())
        return f"variable {variable_name} : std_ulogic_vector({operand.get_data_width()} - 1 downto 0);"

    def get_variable_declarations(self) -> List[str]:
        return [self._get_variable_declaration(operand=i) for i in self.operands]

class LanguageGenerator(ABC):

    @abstractmethod
    def write_signal_declaration(self, name: Optional[LlvmVariableName], data_type: TypeDeclaration) -> None:
        pass

    @abstractmethod
    def instance(self, data: LanguageGeneratorInstanceData) -> None:
        pass

    @abstractmethod
    def write_body(self, text: str) -> None:
        pass

    @abstractmethod
    def return_operation(self, data_type: TypeDeclaration, operands: List[InstructionArgument]) -> None:
        pass

    @abstractmethod
    def generate_code(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        pass
