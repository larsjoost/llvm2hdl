
from abc import ABC, abstractmethod
from typing import Optional

from llvm_declarations import LlvmName, TypeDeclaration

class InstanceInterface(ABC):

    @abstractmethod
    def get_output_signal_name(self) -> LlvmName:
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