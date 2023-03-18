
from abc import ABC, abstractmethod

from llvm_constant import DeclarationBase
from llvm_function import LlvmFunctionContainer

class FileWriterInterface(ABC):

    @abstractmethod
    def write_constant(self, constant: DeclarationBase):
        pass

    @abstractmethod
    def write_reference(self, reference: DeclarationBase, functions: LlvmFunctionContainer):
        pass

