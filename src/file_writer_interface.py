
from abc import ABC, abstractmethod

from llvm_constant import ConstantDeclaration, ReferenceDeclaration


class FileWriterInterface(ABC):

    @abstractmethod
    def write_constant(self, constant: ConstantDeclaration):
        pass

    @abstractmethod
    def write_reference(self, reference: ReferenceDeclaration):
        pass
