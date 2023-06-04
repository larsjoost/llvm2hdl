from dataclasses import dataclass
from typing import List, Optional
from llvm_constant import DeclarationBase, DeclarationContainer
from llvm_type import LlvmType, LlvmVariableName
from vhdl_memory import VhdlMemory

@dataclass
class GlobalsContainer:
    
    declarations: List[DeclarationContainer]

    def get_constants(self) -> List[DeclarationBase]:
        return [i.declaration for i in self.declarations if i.is_constant()]
        
    def get_variables(self) -> List[DeclarationBase]:
        return [i.declaration for i in self.declarations if i.is_variable()]
        
    def get_references(self) -> List[DeclarationBase]:
        return [i.declaration for i in self.declarations if i.is_reference()]

    def _get_match(self, name: Optional[LlvmType]) \
        -> Optional[DeclarationContainer]:
        return next(
            (i for i in self.declarations if i.match(name=name)), None
        )   

    def get_declaration(self, name: Optional[LlvmType]) \
        -> Optional[DeclarationContainer]:
        if name is None or not name.is_name():
            return None
        return self._get_match(name=name)
    
    def get_initialization(self, name: Optional[LlvmVariableName]) \
        -> Optional[List[str]]:
        declaration = self.get_declaration(name=name)
        return None if declaration is None else declaration.get_values()

    def get_data_width(self, name: LlvmVariableName) -> Optional[str]:
        declaration = self.get_declaration(name=name)
        return None if declaration is None else declaration.get_data_width()

    def get_memory_instances(self) -> List[VhdlMemory]:
        memory_instances = []
        for declaration in self.declarations:
            memory_instance = declaration.get_memory_instance()
            if memory_instance is not None:
                memory_instances.append(memory_instance)
        return memory_instances