
from abc import ABC, abstractmethod

from llvm_constant import ConstantDeclaration, ReferenceDeclaration
from llvm_function import LlvmFunctionContainer

class FileWriterInterface(ABC):

    @abstractmethod
    def write_constant(self, constant: ConstantDeclaration):
        pass

    @abstractmethod
    def write_reference(self, reference: ReferenceDeclaration, functions: LlvmFunctionContainer):
        pass

