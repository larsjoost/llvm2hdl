from dataclasses import dataclass
from typing import Dict, Optional
from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmType

@dataclass 
class SourceInfo:
    destination: Optional[LlvmType]
    output_signal_name: LlvmType
    data_type: TypeDeclaration

class SourceInfoMap:
    _map: Dict[LlvmType, SourceInfo]
    
    def __init__(self):
        self._map = {}

    def add(self, type: LlvmType, source_info: SourceInfo):
        self._map[type] = source_info

    def get_source(self, search_source: LlvmType) -> Optional[SourceInfo]:
        return self._map.get(search_source, None)

