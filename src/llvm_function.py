
from dataclasses import dataclass
from typing import List, Optional

from instruction_argument import InstructionArgumentContainer
from llvm_instruction import LlvmInstructionContainer
from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration
from ports import InputPort, OutputPort, Port, PortContainer
from vhdl_memory import VhdlMemory

@dataclass
class LlvmFunction:
    name: str
    arguments: InstructionArgumentContainer
    return_type : TypeDeclaration
    instructions: LlvmInstructionContainer
    def get_input_ports(self) -> List[Port]:
        return [InputPort(name=i.signal_name, data_type=i.data_type) for i in self.arguments.arguments]
    def get_ports(self) -> PortContainer:								
        output_port: List[Port] = [OutputPort(name=LlvmVariableName("m_tdata"), data_type=self.return_type)]
        input_ports: List[Port] = self.get_input_ports()
        return PortContainer(input_ports + output_port)
    def get_external_pointer_names(self) -> List[str]:
        return self.instructions.get_external_pointer_names() + self.arguments.get_pointer_names()
    def get_memory_instance_names(self) -> List[str]:
        return self.instructions.get_memory_instance_names()
    def get_memory_names(self) -> List[str]:
        return self.instructions.get_memory_names()
    def get_memory_drivers(self, memory_instance: VhdlMemory) -> List[str]:
        return self.instructions.get_memory_drivers(memory_instance=memory_instance)

@dataclass
class LlvmFunctionContainer:
    functions: List[LlvmFunction]

    def get_function(self, name: str) -> Optional[LlvmFunction]:
        return next((i for i in self.functions if i.name == name), None)

    def get_function_names(self) -> List[str]:
        return [i.name for i in self.functions]

    def get_external_pointer_names(self) -> List[str]:
        external_pointer_names: List[str] = []
        for i in self.functions:
            external_pointer_names.extend(i.get_external_pointer_names())
        return external_pointer_names
    
    def get_memory_drivers(self, memory_instance: VhdlMemory) -> List[str]:
        memory_drivers = []
        for function in self.functions:
            memory_drivers.extend(function.get_memory_drivers(memory_instance=memory_instance))
        return memory_drivers