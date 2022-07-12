from dataclasses import dataclass
from llvm_declarations import LlvmName, TypeDeclaration

@dataclass 
class SourceInfo:
    destination: LlvmName
    output_signal_name: LlvmName
    data_type: TypeDeclaration

