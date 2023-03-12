from abc import ABC, abstractmethod
from typing import Optional, Tuple

from llvm_type import LlvmType, LlvmTypeFactory

class TypeDeclaration(ABC):
    
    @abstractmethod
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        pass

    @abstractmethod
    def get_data_width(self) -> str:
        pass

    def single_dimension(self) -> bool:
        return True

    def is_pointer(self) -> bool:
        return False

    def is_array(self) -> bool:
        return False

    def is_boolean(self) -> bool:
        return False

    def is_void(self) -> bool:
        return False

    def get_array_index(self) -> Optional[str]:
        return None

    def resolve_type(self, data_type: str) -> LlvmType:
        return LlvmTypeFactory(data_type).resolve()
    
class TypeDeclarationFactory(ABC):

    @abstractmethod
    def match(self) -> bool:
        pass

    @abstractmethod
    def get(self) -> TypeDeclaration:
        pass

