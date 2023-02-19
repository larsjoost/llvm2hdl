from dataclasses import dataclass
from typing import List, Optional
from file_writer_interface import FileWriterInterface
from llvm_constant import DeclarationContainer
from llvm_function import LlvmFunctionContainer
from llvm_type import LlvmVariableName

@dataclass
class ConstantContainer:
    
    declarations: List[DeclarationContainer]

    def write_constants(self, file_writer: FileWriterInterface):
        for i in self.declarations:
            if i.constant_declaration is not None:
                file_writer.write_constant(constant=i.constant_declaration)
    
    def write_references(self, file_writer: FileWriterInterface, functions: LlvmFunctionContainer):
        for i in self.declarations:
            if i.reference_declaration is not None:
                file_writer.write_reference(reference=i.reference_declaration, functions=functions)
    
    def get_declaration(self, name: Optional[LlvmVariableName]) -> Optional[DeclarationContainer]:
        return next(
            (i for i in self.declarations if i.match(name=name)), None
        )   
    
    def get_initialization(self, name: Optional[LlvmVariableName]) -> Optional[List[str]]:
        declaration = self.get_declaration(name=name)
        return None if declaration is None else declaration.get_values()

    def get_data_width(self, name: LlvmVariableName) -> Optional[str]:
        declaration = self.get_declaration(name=name)
        return None if declaration is None else declaration.get_data_width()
