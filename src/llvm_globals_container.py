from dataclasses import dataclass
from typing import List, Optional
from file_writer_interface import FileWriterInterface
from llvm_constant import DeclarationContainer
from llvm_function import LlvmFunctionContainer
from llvm_type import LlvmType, LlvmVariableName

@dataclass
class GlobalsContainer:
    
    declarations: List[DeclarationContainer]

    def write_constants(self, file_writer: FileWriterInterface) -> None:
        for i in self.declarations:
            if i.is_constant():
                file_writer.write_constant(constant=i.declaration)
    
    def write_references(self, file_writer: FileWriterInterface, 
                         functions: LlvmFunctionContainer) -> None:
        for i in self.declarations:
            if i.is_reference():
                file_writer.write_reference(reference=i.declaration, 
                                            functions=functions)
    
    def write_variables(self, file_writer: FileWriterInterface) -> None:
        for i in self.declarations:
            if i.is_variable():
                file_writer.write_variable(variable=i.declaration)
    
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

