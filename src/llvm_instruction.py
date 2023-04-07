
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from function_container_interface import FunctionContainerInterface
from instruction_argument import InstructionArgument
from instruction_interface import LlvmOutputPort, MemoryInterface
from language_generator import LanguageGenerator
from llvm_source_file import LlvmSourceLine

from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration

@dataclass
class LlvmInstructionData:
    source_line: LlvmSourceLine
    
class LlvmInstructionInterface(ABC, LlvmInstructionData):
    def get_destination(self) -> Optional[LlvmVariableName]:
        return None
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_operands(self) -> Optional[List[InstructionArgument]]:
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
    @abstractmethod
    def generate_code(self, generator: LanguageGenerator, container: FunctionContainerInterface) -> None:
        pass    
