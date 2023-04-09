
from dataclasses import dataclass
from typing import List

from llvm_module import LlvmModule


@dataclass
class VhdlModule:
    module: LlvmModule

    def get_external_pointer_names(self) -> List[str]:
        return self.module.get_external_pointer_names()