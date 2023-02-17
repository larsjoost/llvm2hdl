
from dataclasses import dataclass
from typing import List

from instruction_argument import InstructionArgument
from llvm_instruction import LlvmInstruction
from llvm_type_declaration import TypeDeclaration
from ports import InputPort, Port

@dataclass
class LlvmFunction:
    name: str
    arguments: List[InstructionArgument]
    return_type : TypeDeclaration
    instructions: List[LlvmInstruction]
    def get_input_ports(self) -> List[Port]:
        return [InputPort(name=i.signal_name, data_type=i.data_type) for i in self.arguments]

@dataclass
class LlvmFunctionContainer:
    functions: List[LlvmFunction]
