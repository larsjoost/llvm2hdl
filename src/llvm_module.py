
from dataclasses import dataclass
from typing import List
from llvm_constant import DeclarationBase

from llvm_function import LlvmFunctionContainer
from llvm_globals_container import GlobalsContainer
from vhdl_memory import VhdlMemory

@dataclass
class LlvmModule:
    functions: LlvmFunctionContainer
    globals: GlobalsContainer
    
    def get_constants(self) -> List[DeclarationBase]:
        return self.globals.get_constants()
    
    def get_references(self) -> List[DeclarationBase]:
        return self.globals.get_references()
    
    def get_variables(self) -> List[DeclarationBase]:
        return self.globals.get_variables()
    
    def get_external_pointer_names(self) -> List[str]:
        return self.functions.get_external_pointer_names()
    
    def get_globals(self) -> GlobalsContainer:
        return self.globals

    def get_memory_instances(self) -> List[VhdlMemory]:
        return self.globals.get_memory_instances()
    
    def get_memory_drivers(self, pointer_name: str) -> List[str]:
        return self.functions.get_memory_drivers(pointer_name=pointer_name)