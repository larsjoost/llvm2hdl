from dataclasses import dataclass
from typing import List, Tuple, Optional
from instantiation_point import InstantiationPoint
from llvm_source_file import LlvmSourceLine

from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmReferenceName, LlvmType

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
    instruction: LlvmSourceLine
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

