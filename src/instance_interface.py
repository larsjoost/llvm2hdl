
from abc import ABC, abstractmethod

from llvm_declarations import TypeDeclaration

class InstanceInterface(ABC):

    @abstractmethod
    def get_output_signal_name(self) -> str:
        pass

    @abstractmethod
    def get_data_type(self) -> TypeDeclaration:
        pass

    @abstractmethod
    def get_tag_name(self) -> str:
        pass