
from dataclasses import dataclass
from typing import List, Optional

from function_container_interface import FunctionContainerInterface
from instruction_argument import InstructionArgument
from language_generator import LanguageGenerator
from llvm_instruction import LlvmInstructionInterface
from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration
from ports import InputPort, OutputPort, Port, PortContainer

@dataclass
class LlvmFunction:
    name: str
    arguments: List[InstructionArgument]
    return_type : TypeDeclaration
    instructions: List[LlvmInstructionInterface]
    def get_input_ports(self) -> List[Port]:
        return [InputPort(name=i.signal_name, data_type=i.data_type) for i in self.arguments]
    def get_ports(self) -> PortContainer:								
        output_port: List[Port] = [OutputPort(name=LlvmVariableName("m_tdata"), data_type=self.return_type)]
        input_ports: List[Port] = self.get_input_ports()
        return PortContainer(input_ports + output_port)
    def generate_code(self, generator: LanguageGenerator, container: FunctionContainerInterface) -> None:
        for i in self.instructions:
            i.generate_code(generator=generator, container=container)

@dataclass
class LlvmFunctionContainer:
    functions: List[LlvmFunction]

    def get_function(self, name: str) -> Optional[LlvmFunction]:
        return next((i for i in self.functions if i.name == name), None)

    def get_function_names(self) -> List[str]:
        return [i.name for i in self.functions]      