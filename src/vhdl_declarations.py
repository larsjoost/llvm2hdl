from dataclasses import dataclass
from typing import List, Optional, Tuple

from llvm_declarations import TypeDeclaration
from ports import Port

@dataclass
class VhdlDeclarations:

    data_type : TypeDeclaration

    def get_type_declarations(self) -> str:
        if self.data_type.is_boolean():
            type_declaration = "std_ulogic"
        else:
            dimensions: Tuple[int, Optional[str]] = self.data_type.get_dimensions()
            y = dimensions[1]
            type_declaration = "std_ulogic_vector"
            if y is not None:
                type_declaration += "(0 to " + y + " - 1)"
        return type_declaration

    def get_data_width(self) -> str:
        dimensions: Tuple[int, Optional[str]] = self.data_type.get_dimensions()
        x = dimensions[0]
        y = dimensions[1]
        if y is None:
            return str(x)
        return y if (x == 1) else str(x) + "*" + y

    def get_initialization(self, values: List[str]) -> str:
        return "get(integer_array_t'(" + ", ".join(values) + "), " + self.get_data_width() + ")"

@dataclass
class VhdlSignal:
    instance : str
    name : str
    type : VhdlDeclarations
    def write_signal(self, file_handle):
        print("signal " + self.name + " : tag_t;", file=file_handle)
    def get_record_item(self) -> Tuple[str, str]:
        return (self.instance, ": " + self.type.get_type_declarations() + ";")
    def get_data_width(self) -> str:
        return self.type.get_data_width()
