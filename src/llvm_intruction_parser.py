
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from instruction_interface import InstructionInterface
from llvm_destination import LlvmDestination
from llvm_globals_container import GlobalsContainer
from llvm_source_file import LlvmSourceLine

from messages import Messages


@dataclass
class LlvmInstructionParserArguments:
    instruction: str
    destination: LlvmDestination
    constants: GlobalsContainer

class LlvmInstructionParserInterface(ABC):

    def __init__(self):
        self._msg = Messages()

    @abstractmethod
    def parse(self, arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> Optional[InstructionInterface]:
        pass

    @abstractmethod
    def match(self, instruction: List[str]) -> bool:
        pass

