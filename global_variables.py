from dataclasses import dataclass
from typing import Dict


@dataclass
class GlobalVariable:
    name: str
    data_type: str
    definition: str

class GlobalVariables:
    
    _global_variables: Dict[str, GlobalVariable] = {}

    def add(self, name: str, data_type: str, definition: str):
        self._global_variables[name] = GlobalVariable(name=name, data_type=data_type, definition=definition)
