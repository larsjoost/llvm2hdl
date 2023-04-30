
from dataclasses import dataclass
from typing import List

from llvm_constant import DeclarationBase
from vhdl_declarations import VhdlDeclarations
from vhdl_memory import VhdlMemory

@dataclass
class VhdlFileWriterConstant:
    constant : DeclarationBase
    def _get_values(self) -> List[str]:
        data_type = self.constant.get_type()
        assert data_type is not None
        values = self.constant.get_values()
        return [""] if values is None else values
    def _get_initialization(self) -> str:
        data_type = self.constant.get_type()
        assert data_type is not None
        vhdl_declaration = VhdlDeclarations(data_type=data_type)
        values = self._get_values()
        return vhdl_declaration.get_initialization(values=values)
    def _get_initialization_array(self) -> str:
        data_type = self.constant.get_type()
        assert data_type is not None
        vhdl_declaration = VhdlDeclarations(data_type=data_type)
        values = self._get_values()
        return vhdl_declaration.get_initialization_array(values=values)
    def get_constant_declaration(self) -> str:
        initialization = self._get_initialization()
        name = self.constant.get_name()
        return f"constant {name} : std_ulogic_vector := {initialization};"
    def get_memory_instance(self) -> VhdlMemory:
        initialization = self._get_initialization_array()
        size_bytes = f"{self.constant.get_data_width()} / 8"
        return VhdlMemory(name=self.constant.get_name(), size_bytes=size_bytes, initialization=initialization)
