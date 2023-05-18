from dataclasses import dataclass
from typing import List, Tuple, Optional
from instantiation_point import InstantiationPoint
from llvm_source_file import LlvmSourceLine

from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmReferenceName, LlvmType
from vhdl_declarations import VhdlDeclarations
from vhdl_memory import VhdlMemory

@dataclass
class Constant:
    value: str
    data_type: TypeDeclaration

@dataclass
class DeclarationBase:
    instruction: LlvmSourceLine
    instantiation_point: InstantiationPoint
    name: LlvmType
    def get_name(self) -> str:
        return self.name.translate_name()
    def get_type(self) -> Optional[TypeDeclaration]:
        return None
    def _is_name(self, name: LlvmType) -> bool:
        return self.name.equals(other=name)
    def match(self, name: Optional[LlvmType]) -> bool:
        return False if name is None else self._is_name(name=name)
    def get_values(self) -> Optional[List[str]]:
        return None
    def get_data_width(self) -> Optional[str]:
        return None
    def is_reference(self) -> bool:
        return False
    def is_constant(self) -> bool:
        return False
    def is_variable(self) -> bool:
        return False
    def get_reference(self) -> Optional[str]:
        return None
    def is_register(self) -> bool:
        return False
    def get_memory_instance(self) -> Optional[VhdlMemory]:
        return None

@dataclass
class ConstantDeclaration(DeclarationBase):
    type: TypeDeclaration
    values: List[Constant]
    def get_type(self) -> Optional[TypeDeclaration]:
        return self.type
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.type.get_dimensions()
    def get_values(self) -> Optional[List[str]]:
        return [i.value for i in self.values]
    def get_data_width(self) -> Optional[str]:
        return self.type.get_data_width()
    def is_constant(self) -> bool:
        return True
    def get_memory_instance(self) -> Optional[VhdlMemory]:
        values = self.get_values()
        assert values is not None
        initialization = VhdlDeclarations(data_type=self.type).get_initialization_array(values=values)
        data_width = self.get_data_width()
        assert data_width is not None
        size_bytes = f"{data_width}/8"
        return VhdlMemory(size_bytes=size_bytes, initialization=initialization, name=self.get_name())
    
@dataclass
class ReferenceDeclaration(DeclarationBase):
    reference: LlvmReferenceName
    def is_reference(self) -> bool:
        return True
    def get_reference(self) -> Optional[str]:
        return self.reference.translate_name()

@dataclass
class ClassDeclaration(DeclarationBase):
    type: TypeDeclaration
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.type.get_dimensions()
    def get_data_width(self) -> Optional[str]:
        return self.type.get_data_width()

@dataclass
class GlobalVariableDeclaration(DeclarationBase):
    type: TypeDeclaration
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.type.get_dimensions()
    def get_data_width(self) -> Optional[str]:
        return self.type.get_data_width()
    def is_variable(self) -> bool:
        return True
    def is_register(self) -> bool:
        return True

@dataclass
class DeclarationContainer:
    declaration: DeclarationBase
    def match(self, name: Optional[LlvmType]) -> bool:
        return self.declaration.match(name=name)
    def get_values(self) -> Optional[List[str]]:
        return self.declaration.get_values()
    def get_data_width(self) -> Optional[str]:
        return self.declaration.get_data_width()
    def is_reference(self) -> bool:
        return self.declaration.is_reference()
    def is_constant(self) -> bool:
        return self.declaration.is_constant()
    def is_variable(self) -> bool:
        return self.declaration.is_variable()
    def is_register(self) -> bool:
        return self.declaration.is_register()
    def get_memory_instance(self) -> Optional[VhdlMemory]:
        return self.declaration.get_memory_instance()
