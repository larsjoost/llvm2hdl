
from types import FrameType
from typing import Optional

from instantiation_point import InstantiationPoint

class VhdlCodeGenerator:
    
    def get_vhdl_name(self, llvm_name: str) -> str:
        name = llvm_name.replace("%", "").replace("@", "").strip("_").replace("__", "_").replace(".", "_")
        return "nil" if name == "_" else name

    def get_variable_name(self, name: str) -> str:
        return f"{name}_v"

    def translate_variable_name(self, name: str) -> str:
        return f"var_{name}"

    def get_destination_variable_name(self, llvm_name: str) -> str:
        return self.translate_variable_name(name = self.get_vhdl_name(llvm_name))
    
    def get_signal_name(self, name: str) -> str:
        return f"{name}_i"

    def _get_declaration(self, declaration_type: str, name: str, data_width: str) -> str:
        return f"{declaration_type} {name} : std_ulogic_vector({data_width} - 1 downto 0);"

    def get_variable_declaration(self, name: str, data_width: str) -> str:
        name = self.get_variable_name(name)
        return self._get_declaration(declaration_type="variable", name=name, data_width=data_width)

    def get_signal_declaration(self, name: str, data_width: str) -> str:
        name = self.get_variable_name(name)
        return self._get_declaration(declaration_type="signal", name=name, data_width=data_width)

    def get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        instantiation_point = InstantiationPoint(current_frame=current_frame)
        return f"-- {instantiation_point.show()}: "
