from dataclasses import dataclass
from typing import List, Tuple, Optional
from llvm_source_file import LlvmSourceLine

from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmReferenceName, LlvmType

@dataclass
class Constant:
    value: str
    data_type: TypeDeclaration

@dataclass
class ConstantDeclarationBase:
    name: LlvmType
    def get_name(self) -> str:
        return self.name.get_name()
    def _is_name(self, name: LlvmType) -> bool:
        return self.name.get_name() == name.get_name()
    def match(self, name: Optional[LlvmType]) -> bool:
        return False if name is None else self._is_name(name=name)
    def get_values(self) -> Optional[List[str]]:
        return None
    def get_data_width(self) -> Optional[str]:
        return None
    def is_reference(self) -> bool:
        return False

@dataclass
class ConstantDeclaration(ConstantDeclarationBase):
    type: TypeDeclaration
    values: List[Constant]
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.type.get_dimensions()
    def get_values(self) -> Optional[List[str]]:
        return [i.value for i in self.values]
    def get_data_width(self) -> Optional[str]:
        return self.type.get_data_width()

@dataclass
class ReferenceDeclaration(ConstantDeclarationBase):
    reference: LlvmReferenceName
    def is_reference(self) -> bool:
        return True

@dataclass
class ClassDeclaration(ConstantDeclarationBase):
    type: TypeDeclaration
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.type.get_dimensions()
    def get_data_width(self) -> Optional[str]:
        return self.type.get_data_width()

@dataclass
class DeclarationContainer:
    instruction: LlvmSourceLine
    constant_declaration: Optional[ConstantDeclaration] = None
    reference_declaration: Optional[ReferenceDeclaration] = None
    class_declaration: Optional[ClassDeclaration] = None
    def match(self, name: Optional[LlvmType]) -> bool:
        return (self.constant_declaration is not None and self.constant_declaration.match(name=name)) or \
        (self.reference_declaration is not None and self.reference_declaration.match(name=name)) or \
        (self.class_declaration is not None and self.class_declaration.match(name=name))
    def get_values(self) -> Optional[List[str]]:
        if self.constant_declaration is not None:
            return self.constant_declaration.get_values()
        return None
    def get_data_width(self) -> Optional[str]:
        if self.constant_declaration is not None:
            return self.constant_declaration.get_data_width()
        if self.class_declaration is not None:
            return self.class_declaration.get_data_width()
        return None
