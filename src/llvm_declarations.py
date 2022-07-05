
from abc import ABC, abstractmethod
from typing import Optional, Tuple
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

    def get_array_index(self) -> Optional[str]:
        return None

    def get_reference_arguments(self) -> Tuple[str, Optional[str]]:
        """
        Return tuple consisting of data_width and pointer index
        """        
        pass

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
        # self.data_type = "[3 x i32]*"
        x = self.data_type.replace("[", "").replace("]", "").replace("*", "").split("x")
        return (int(x[0]), self._get_data_width(data_type=x[1]))

    def get_data_width(self) -> str:
        x, data_width = self.get_dimensions()
        if x > 1:
            data_width = str(x) + "*" + data_width
        return data_width

    def get_reference_arguments(self) -> Tuple[str, Optional[str]]:
        data_width = self.get_data_width()
        array_index = None
        return data_width, array_index

    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self) -> str:
        return str(vars(self))


class LlvmArrayDeclaration(TypeDeclaration):
    
    data_type : LlvmDeclaration
    index : str

    def __init__(self, data_type: LlvmDeclaration, index: str):
        self.data_type = data_type
        self.index = index

    def get_dimensions(self) -> Tuple[int, str]:
        return self.data_type.get_dimensions()

    def single_dimension(self) -> bool:
        return False

    def is_array(self) -> bool:
        return True

    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self) -> str:
        return str(vars(self))

    def get_array_index(self) -> str:
        return self.index

    def get_reference_arguments(self) -> Tuple[str, Optional[str]]:
        data_width, _ = self.data_type.get_reference_arguments()
        return data_width, self.get_array_index()

@dataclass
class LlvmType:
    def __str__(self) -> str:
        pass
    def is_integer(self) -> bool:
        return False

@dataclass(frozen=True)
class LlvmName(LlvmType):
    """
    Example %0, %a
    """
    name: str
    def __str__(self) -> str:
        return self.name.replace("%", "")

@dataclass(frozen=True)
class LlvmInteger(LlvmType):
    value: int
    def __str__(self) -> str:
        return str(self.value)
    def is_integer(self) -> bool:
        return True

class LlvmTypeFactory:
    text: str
    def __init__(self, text: str):
        self.text = text
    def resolve(self) -> LlvmType:
        if "%" in self.text:
            return LlvmName(self.text)
        try:
            value = int(self.text)
            return LlvmInteger(value)
        except ValueError:
            pass
        raise ValueError("Unknown LlvmType")

class VectorDeclaration(TypeDeclaration):
    
    data_width: Optional[str]

    def __init__(self, data_width: Optional[str] = None) -> None:
        self.data_width = data_width

    def get_dimensions(self) -> Tuple[int, str]:
        return (1, self.data_width)

class BooleanDeclaration(TypeDeclaration):
    
    def get_dimensions(self) -> Tuple[int, str]:
        return (1, "1")

    def is_boolean(self) -> bool:
        return True
