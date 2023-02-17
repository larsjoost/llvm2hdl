
from dataclasses import dataclass

from llvm_function import LlvmFunctionContainer
from llvm_constant_container import ConstantContainer

@dataclass
class LlvmModule:
    functions: LlvmFunctionContainer
    constants: ConstantContainer
    def write_constants(self, file_writer):
        self.constants.write_constants(file_writer=file_writer)
    def write_references(self, file_writer):
        self.constants.write_references(file_writer=file_writer, functions=self.functions)

