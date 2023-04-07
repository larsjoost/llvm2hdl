
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from instruction_interface import InstructionInterface
from llvm_globals_container import GlobalsContainer
from llvm_source_file import LlvmSourceLine

from llvm_type import LlvmVariableName
from messages import Messages


@dataclass
class LlvmInstructionParserArguments:
    instruction: str
    destination: Optional[LlvmVariableName]
    constants: GlobalsContainer

class LlvmInstructionParserInterface(ABC):

    def __init__(self):
        self._msg = Messages()

    @abstractmethod
    def parse(self, arguments: LlvmInstructionParserArguments, source_line: LlvmSourceLine) -> Optional[InstructionInterface]:
        pass

    @abstractmethod
    def match(self, instruction: List[str]) -> bool:
        pass

