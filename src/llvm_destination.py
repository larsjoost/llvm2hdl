
from dataclasses import dataclass
from typing import Optional

from llvm_type import LlvmVariableName

@dataclass
class LlvmDestination:
    name: Optional[LlvmVariableName]

    def get_translated_name(self) -> str:
        assert self.name is not None
        return self.name.translate_name()
