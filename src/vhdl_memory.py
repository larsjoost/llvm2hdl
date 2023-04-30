
from dataclasses import dataclass
from typing import List


@dataclass
class VhdlMemory:
    names: List[str]
    instance_names: List[str]