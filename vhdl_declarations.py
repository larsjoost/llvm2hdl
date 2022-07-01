from dataclasses import dataclass
from typing import List, Tuple

from llvm_declarations import TypeDeclaration

@dataclass
class VhdlDeclarations:

    data_type : TypeDeclaration

    def get_type_declarations(self) -> str:
        if self.data_type.is_boolean():
            type_declaration = "std_ulogic"
        else:
            dimensions: Tuple[int, str] = self.data_type.get_dimensions()
            x = str(dimensions[0])
            y = dimensions[1]
            if self.data_type.single_dimension():
                type_declaration = "std_ulogic_vector(0 to " + dimensions[1] + " - 1)"
            elif self.data_type.is_pointer():
                type_declaration = "memory_i" + y
            else:
                type_declaration = "memory_i" + y + "(0 to " + x + " - 1)"
        return type_declaration

    def get_initialization(self, values: List[str]) -> str:
        dimensions: Tuple[int, str] = self.data_type.get_dimensions()
        if dimensions[0] == 1:
            return ""
        return "set_memory_i" + dimensions[1] + "((" + ", ".join(values) + "))"

    def get_data_width(self) -> str:
        dimensions: Tuple[int, str] = self.data_type.get_dimensions()
        x = dimensions[0]
        scale = "" if x == 1 else str(x) + "*"
        return scale + dimensions[1]