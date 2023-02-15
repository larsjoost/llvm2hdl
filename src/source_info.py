from dataclasses import dataclass
from typing import Optional
from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmType

@dataclass 
class SourceInfo:
    destination: Optional[LlvmType]
    output_signal_name: LlvmType
    data_type: TypeDeclaration

