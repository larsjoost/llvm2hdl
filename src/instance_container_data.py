from dataclasses import dataclass
from typing import List

from instance_data import InstanceData

@dataclass
class InstanceContainerData:
    instances: List[InstanceData]    
