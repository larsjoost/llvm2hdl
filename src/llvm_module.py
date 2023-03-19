
from dataclasses import dataclass

from llvm_function import LlvmFunctionContainer
from llvm_globals_container import GlobalsContainer

@dataclass
class LlvmModule:
    functions: LlvmFunctionContainer
    globals: GlobalsContainer
    def write_globals(self, file_writer):
        self.globals.write_constants(file_writer=file_writer)
        self.globals.write_references(file_writer=file_writer, functions=self.functions)
        self.globals.write_variables(file_writer=file_writer)
