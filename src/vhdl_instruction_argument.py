
from dataclasses import dataclass
from typing import Optional, Tuple
from instruction_argument import InstructionArgument

from llvm_type import LlvmType
from llvm_type_declaration import TypeDeclaration
from vhdl_instance_name import VhdlInstanceName

@dataclass
class VhdlInstructionArgument:
    signal_name: str
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
        return self.signal_name
    def get_value(self) -> str:
        if self.is_integer():
            hexadecimal = f'{int(self.signal_name):x}'
            return f'x"{hexadecimal}"'
        return self.signal_name
    def get_data_width(self) -> str:
        return self.data_type.get_data_width()
    def is_integer(self) -> bool:
        return self.signal_name.isdigit()
        
class VhdlInstructionArgumentFactory:

    def get(self, instruction_argument: InstructionArgument) -> VhdlInstructionArgument:
        name = instruction_argument.signal_name.get_name()
        signal_name = VhdlInstanceName(name=name).get_entity_name()
        return VhdlInstructionArgument(signal_name=signal_name, data_type=instruction_argument.data_type, 
        unnamed=instruction_argument.unnamed, port_name=instruction_argument.port_name)