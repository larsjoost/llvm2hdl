from dataclasses import dataclass
from typing import Optional, Union
from llvm_type import LlvmVariableName

from llvm_type_declaration import TypeDeclaration
from vhdl_declarations import VhdlDeclarations

@dataclass
class LlvmOutputPort:
    data_type : TypeDeclaration
    port_name: Optional[Union[LlvmVariableName, str]] = None
    def get_type_declarations(self) -> str:
        return VhdlDeclarations(self.data_type).get_type_declarations()
    def is_pointer(self) -> bool:
        return False
    def get_name(self) -> Optional[str]:
        if isinstance(self.port_name, LlvmVariableName):
            return self.port_name.translate_name()
        return self.port_name
    def is_void(self) -> bool:
        return self.data_type.is_void()

@dataclass
class LlvmMemoryOutputPort(LlvmOutputPort):
    def is_pointer(self) -> bool:
        return True
