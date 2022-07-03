from dataclasses import dataclass
from typing import List, Tuple

from llvm_declarations import TypeDeclaration
from ports import Port

@dataclass
class VhdlDeclarations:

    data_type : TypeDeclaration

    def get_type_declarations(self) -> str:
        if self.data_type.is_boolean():
            type_declaration = "std_ulogic"
        else:
            dimensions: Tuple[int, str] = self.data_type.get_dimensions()
            y = dimensions[1]
            type_declaration = "std_ulogic_vector"
            if y is not None:
                type_declaration += "(0 to " + y + " - 1)"
        return type_declaration

    def get_data_width(self) -> str:
        dimensions: Tuple[int, str] = self.data_type.get_dimensions()
        x = dimensions[0]
        scale = "" if x == 1 else str(x) + "*"
        return scale + dimensions[1]


