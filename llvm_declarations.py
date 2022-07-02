
from abc import ABC, abstractmethod
from typing import Tuple
from dataclasses import dataclass

class TypeDeclaration(ABC):
    @abstractmethod
    def get_dimensions(self) -> Tuple[int, str]:
        pass

    def single_dimension(self) -> bool:
        return True

    def is_pointer(self) -> bool:
        return False

    def is_array(self) -> bool:
        return False

    def is_boolean(self) -> bool:
        return False

class LlvmDeclaration(TypeDeclaration):
    """
    data_type is one of i1, i32, i64, i32*, float, 3 x i32 
    """
    data_type: str

    def __init__(self, data_type: str) -> None:
        self.data_type = data_type

    def _get_data_width(self, data_type: str) -> str:
        x = data_type.strip()
        x = x.replace("*", "")
        if x[0] == "i":
            return x[1:]
        data_types = {'float': "32"}
        return data_types[x]

    def is_pointer(self) -> bool:
        return "*" in self.data_type
    
    def is_array(self) -> bool:
        return " x " in self.data_type

    def single_dimension(self) -> bool:
        return not (self.is_pointer() or self.is_array())

    def get_dimensions(self) -> Tuple[int, str]:
        if not self.is_array():
            return (1, self._get_data_width(data_type=self.data_type))
        x = self.data_type.split("x")
        return (int(x[0]), self._get_data_width(data_type=x[1]))

    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self) -> str:
        return str(vars(self))

@dataclass(frozen=True)
class LlvmName:
    """
    Example %0, %a
    """
    name: str
    def get_value(self) -> str:
        return self.name.replace("%", "")

class VectorDeclaration(TypeDeclaration):
    
    data_width: str

    def __init__(self, data_width: str) -> None:
        self.data_width = data_width

    def get_dimensions(self) -> Tuple[int, str]:
        return (1, self.data_width)

class BooleanDeclaration(TypeDeclaration):
    
    def get_dimensions(self) -> Tuple[int, str]:
        return (1, "1")

    def is_boolean(self) -> bool:
        return True
