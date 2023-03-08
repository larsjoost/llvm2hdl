from dataclasses import dataclass
from typing import List, Tuple

from llvm_type_declaration import TypeDeclaration

@dataclass
class VhdlDeclarations:

    data_type : TypeDeclaration

    def get_type_declarations(self) -> str:
        if self.data_type.is_boolean():
            type_declaration = "std_ulogic"
        else:
            data_width = self.data_type.get_data_width()
            type_declaration = "std_ulogic_vector"
            if data_width is not None:
                type_declaration += f"(0 to {data_width} - 1)"
        return type_declaration

    def get_data_width(self) -> str:
        return self.data_type.get_data_width()

    def get_initialization(self, values: List[str]) -> str:
        arguments = ", ".join(values)
        return f"get(integer_array_t'({arguments}), {self.get_data_width()})"

    def is_void(self) -> bool:
        return self.data_type.is_void()

@dataclass
class VhdlSignal:
    instance : str
    name : str
    type : VhdlDeclarations
    def get_signal_declaration(self) -> str:
        return f"signal {self.name} : tag_t;"
    def get_record_item(self) -> Tuple[str, str]:
        return self.instance, f": {self.type.get_type_declarations()};"
    def get_data_width(self) -> str:
        return self.type.get_data_width()
    def is_void(self) -> bool:
        return self.type.is_void()
