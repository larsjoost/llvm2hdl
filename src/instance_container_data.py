from dataclasses import dataclass
from typing import List, Tuple, Optional

from instance_data import InstanceData

@dataclass
class InstanceContainerData:
    instances: List[InstanceData]
    
    def get_return_data_width(self) -> Optional[str]:
        dimensions : Tuple[int, Optional[str]] = self.return_data_type.get_dimensions()
        return dimensions[1]

    def get_return_instruction_driver(self) -> str:
        return self.instances[-1].instance_name