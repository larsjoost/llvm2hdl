
from dataclasses import dataclass
from typing import Optional, Tuple
from instruction_argument import InstructionArgument
from llvm_constant import DeclarationContainer
from llvm_globals_container import GlobalsContainer
from llvm_type_declaration import TypeDeclaration
from vhdl_instance_name import VhdlInstanceName

from vhdl_type import VhdlType, VhdlTypeFactory

@dataclass
class VhdlInstructionArgument:
    signal_name: str
    vhdl_type: VhdlType
    data_type : TypeDeclaration
    unnamed : bool
    port_name: Optional[str]
    global_declaration: Optional[DeclarationContainer]
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
        return self.vhdl_type.get_value()
    def get_data_width(self) -> str:
        return self.data_type.get_data_width()
    def is_integer(self) -> bool:
        return self.vhdl_type.is_integer()
    def get_input_port_signal_name(self) -> str:
        signal_name = self.vhdl_type.get_name()
        array_index = self.get_array_index()
        if array_index is not None:
            signal_name += f"_{array_index}"
        return signal_name
    def access_register(self) -> bool:
        if self.global_declaration is None:
            return False
        return self.global_declaration.is_register()

class VhdlInstructionArgumentFactory:

    def get(self, instruction_argument: InstructionArgument, globals: GlobalsContainer) -> VhdlInstructionArgument:
        vhdl_type = VhdlTypeFactory(llvm_type=instruction_argument.signal_name).resolve()
        name = instruction_argument.signal_name.translate_name()
        signal_name = VhdlInstanceName(name=name).get_entity_name()
        global_declaration = globals.get_declaration(name=instruction_argument.signal_name)
        return VhdlInstructionArgument(signal_name=signal_name, vhdl_type=vhdl_type, 
                                       data_type=instruction_argument.data_type, 
                                       unnamed=instruction_argument.unnamed, 
                                       port_name=instruction_argument.port_name,
                                       global_declaration=global_declaration)
