        
from dataclasses import dataclass

from llvm_constant import DeclarationBase
from vhdl_code_generator import VhdlCodeGenerator


@dataclass
class VhdlFileWriterVariable:
    variable : DeclarationBase
    def write_variable(self) -> str:
        comment = VhdlCodeGenerator().get_comment() 
        name = self.variable.get_name()
        data_width = self.variable.get_data_width()
        return f"""
{comment} Global variables
signal {name} : std_ulogic_vector(0 to {data_width} - 1);
        """
