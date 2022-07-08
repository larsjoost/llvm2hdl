from dataclasses import dataclass
from typing import List, Tuple, Optional

from instance_data import InstanceData
from llvm_declarations import TypeDeclaration


@dataclass
class InstanceContainerData:
    instances: List[InstanceData]
    return_instruction_driver: str
    return_data_type: TypeDeclaration

    def get_return_data_width(self) -> Optional[str]:
        dimensions : Tuple[int, Optional[str]] = self.return_data_type.get_dimensions()
        return dimensions[1]
