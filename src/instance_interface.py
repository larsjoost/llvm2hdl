
from abc import ABC, abstractmethod
from typing import Optional

from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration

class InstanceInterface(ABC):

    @abstractmethod
    def get_output_signal_name(self) -> LlvmVariableName:
        pass

    @abstractmethod
    def get_data_type(self) -> Optional[TypeDeclaration]:
        pass

    @abstractmethod
    def get_tag_name(self) -> str:
        pass

    @abstractmethod
    def get_instance_index(self) -> int:
        pass

    @abstractmethod
    def get_instance_name(self) -> str:
        pass