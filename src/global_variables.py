from dataclasses import dataclass
from typing import Dict
from file_writer import FileWriter
from llvm_parser import LlvmParser

@dataclass
class GlobalVariable:
    name: str
    data_type: str
    definition: str

class GlobalVariables:
    
    _global_variables: Dict[str, GlobalVariable] = {}

    def add(self, name: str, data_type: str, definition: str):
        self._global_variables[name] = GlobalVariable(name=name, data_type=data_type, definition=definition)

    def write(self, file_writer: FileWriter):
        _llvm_parser = LlvmParser()
        for i in self._global_variables.values():
            _constant = _llvm_parser.get_constant_declaration(i.definition)
            file_writer.write_constant(_constant)
