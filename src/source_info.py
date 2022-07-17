from dataclasses import dataclass
from typing import Optional
from llvm_declarations import LlvmName, LlvmType, TypeDeclaration

@dataclass 
class SourceInfo:
    destination: Optional[LlvmType]
    output_signal_name: LlvmType
    data_type: TypeDeclaration

