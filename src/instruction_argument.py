
from dataclasses import dataclass
from typing import Optional, Tuple

from llvm_type import LlvmType
from llvm_type_declaration import TypeDeclaration

@dataclass
class InstructionArgument:
    signal_name: LlvmType
    data_type : TypeDeclaration
    unnamed : bool = False 
    port_name: Optional[str] = None
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.data_type.get_dimensions()
    def single_dimension(self) -> bool:
        return self.data_type.single_dimension()
    def is_pointer(self) -> bool:
        return self.data_type.is_pointer()
    def get_array_index(self) -> Optional[str]:
        return self.data_type.get_array_index()
    def get_name(self) -> str:
        return self.signal_name.get_name()
    def get_value(self) -> str:
        return self.signal_name.get_value()
    def get_data_width(self) -> str:
        return self.data_type.get_data_width()
    def is_integer(self) -> bool:
        if isinstance(self.signal_name, LlvmType):
            return self.signal_name.is_integer()
        return False

