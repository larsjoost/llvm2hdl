

from dataclasses import dataclass
from typing import List
from llvm_function import LlvmFunction
from ports import PortContainer
from vhdl_code_generator import VhdlCodeGenerator
from vhdl_instruction import VhdlInstruction, VhdlInstructionContainer

@dataclass
class VhdlFunction:

    function: LlvmFunction

    def get_entity_name(self) -> str:
        return VhdlCodeGenerator().get_vhdl_name(self.function.name)

    def get_ports(self) -> PortContainer:
        return self.function.get_ports()

    def get_instructions(self) -> VhdlInstructionContainer:
        instructions = [VhdlInstruction(i) for i in self.function.instructions.instructions]
        return VhdlInstructionContainer(instructions)

    def get_memory_names(self) -> List[str]:
        return self.function.get_memory_names()
    
    def get_memory_instance_names(self) -> List[str]:
        return self.function.get_memory_instance_names()
    
