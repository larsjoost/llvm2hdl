from dataclasses import dataclass
from llvm_declarations import LlvmName, LlvmType, TypeDeclaration

@dataclass 
class SourceInfo:
    destination: LlvmName
    output_signal_name: LlvmName
    data_type: TypeDeclaration

