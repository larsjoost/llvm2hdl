from dataclasses import dataclass
from typing import List, Tuple, Optional
from function_logger import log_entry_and_exit

from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmName

@dataclass
class Constant:
    value: str
    data_type: TypeDeclaration

@dataclass
class ConstantDeclaration:
    name: str
    type: TypeDeclaration
    values: List[Constant]
    def get_name(self) -> str:
        return self.name.rsplit(".", maxsplit=1)[-1].strip()
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.type.get_dimensions()
    def get_values(self) -> List[str]:
        return [i.value for i in self.values]
    def _is_name(self, name: str) -> bool:
        return self.get_name().strip() == name.strip()
    def match(self, name: Optional[LlvmName]) -> bool:
        return False if name is None else self._is_name(name=name.get_name())
    def get_data_width(self) -> Optional[str]:
        return None

@dataclass
class ConstantContainer:
    
    constants: List[ConstantDeclaration]
    
    def write_constants(self, file_writer):
        for i in self.constants:
            file_writer.write_constant(constant=i)
    
    def get_constant_declaration(self, name: Optional[LlvmName]) -> Optional[ConstantDeclaration]:
        return next(
            (i for i in self.constants if i.match(name=name)), None
        )   
    
    def get_initialization(self, name: Optional[LlvmName]) -> Optional[List[str]]:
        constant_declaration = self.get_constant_declaration(name=name)
        if constant_declaration is None:
            return None
        return constant_declaration.get_values()

    def get_data_width(self, name: LlvmName) -> Optional[str]:
        constant_declaration = self.get_constant_declaration(name=name)
        if constant_declaration is None:
            return None
        return constant_declaration.get_data_width()

