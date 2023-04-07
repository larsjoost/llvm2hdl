from dataclasses import dataclass

from vhdl_code_generator import VhdlCodeGenerator

@dataclass
class VhdlInstanceName:
    name: str
    library: str = "work"
    def get_entity_name(self) -> str:
        return VhdlCodeGenerator().get_vhdl_name(self.name)
