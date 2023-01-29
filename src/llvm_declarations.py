
import contextlib
from abc import ABC, abstractmethod
import re
from typing import Optional, Tuple
from dataclasses import dataclass

from pydantic import BaseModel, validator

from messages import Messages

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

class TypeDeclarationFactory(ABC):

    @abstractmethod
    def match(self) -> bool:
        pass

    @abstractmethod
    def get(self) -> TypeDeclaration:
        pass

    
class LlvmVoidDeclaration(TypeDeclaration):

    def get_dimensions(self) -> Tuple[int, str]:
        return 1, self.get_data_width()

    def is_void(self) -> bool:
        return True

    def get_data_width(self) -> str:
        return "0"

@dataclass
class LlvmVoidDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str

    def match(self):
        return self.data_type == "void"

    def get(self) -> TypeDeclaration:
        return LlvmVoidDeclaration()

class LlvmFloatDeclaration(TypeDeclaration):
    """
    data_type is one of float 
    """

    def get_dimensions(self) -> Tuple[int, str]:
        return 1, self.get_data_width()

    def get_data_width(self) -> str:
        return "32"

@dataclass
class LlvmFloatDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str

    def match(self):
        return self.data_type == "float"

    def get(self) -> TypeDeclaration:
        return LlvmFloatDeclaration()

@dataclass
class LlvmIntegerDeclaration(TypeDeclaration):

    data_width: int
    
    def __post_init__(self) -> None:
        assert isinstance(self.data_width, int), f"data_width = {self.data_width} is not an integer"
    
    def get_data_width(self) -> str:
        return str(self.data_width)

    def get_dimensions(self) -> Tuple[int, str]:
        return 1, str(self.get_data_width())        

@dataclass
class LlvmIntegerDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str

    def match(self) -> bool:
        return bool(re.match("^i\d+", self.data_type))

    def get(self) -> TypeDeclaration:
        data_width = int(self.data_type[1:])
        return LlvmIntegerDeclaration(data_width=data_width)

@dataclass
class LlvmConstantDeclaration(TypeDeclaration):

    number: str
    
    def get_data_width(self) -> str:
        return self.number

    def get_dimensions(self) -> Tuple[int, str]:
        return 1, self.get_data_width()        

@dataclass
class LlvmConstantDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str

    def match(self) -> bool:
        return self.data_type.isnumeric()

    def get(self) -> TypeDeclaration:
        return LlvmConstantDeclaration(number=self.data_type)

@dataclass
class LlvmPointerDeclaration(TypeDeclaration):
    
    def is_pointer(self) -> bool:
        return True
    
    def single_dimension(self) -> bool:
        return False

    def get_dimensions(self) -> Tuple[int, str]:
        return 1, self.get_data_width()
        
    def get_data_width(self) -> str:
        return "32"

@dataclass
class LlvmPointerDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str
    
    def match(self) -> bool:
        return self.data_type == "ptr" or self.data_type.endswith("*")

    def get(self) -> TypeDeclaration:
        return LlvmPointerDeclaration()

@dataclass
class LlvmArrayDeclaration(TypeDeclaration):
    """
    Declaration: <index> x <data_type>
    Example:
    3 x i32 
    """
    x: TypeDeclaration
    y: TypeDeclaration

    def _get_dimensions(self) -> Tuple[str, str]:
        return self.x.get_data_width(), self.y.get_data_width()

    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        index, data_type = self._get_dimensions()
        return int(index), data_type

    def single_dimension(self) -> bool:
        return False

    def is_array(self) -> bool:
        return True

    def get_array_index(self) -> str:
        index, data_type = self._get_dimensions()
        return index

    def get_data_width(self) -> str:
        index, data_type = self._get_dimensions()
        return f"{index}*{data_type}"

@dataclass
class LlvmArrayDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str
    
    def match(self) -> bool:
        return " x " in self.data_type

    def get(self) -> TypeDeclaration:
        x = self.data_type.split(" x ")
        y = LlvmIntegerDeclarationFactory(data_type=x[1]).get()
        return LlvmArrayDeclaration(x=LlvmConstantDeclaration(x[0]), y=y)

class LlvmDeclarationFactory:

    def get(self, data_type: str) -> TypeDeclaration:
        declaration_types = [
            LlvmVoidDeclarationFactory(data_type=data_type),
            LlvmFloatDeclarationFactory(data_type=data_type),
            LlvmPointerDeclarationFactory(data_type=data_type),
            LlvmIntegerDeclarationFactory(data_type=data_type),
            LlvmArrayDeclarationFactory(data_type=data_type)
        ]    
        for i in declaration_types:
            if i.match():
                return i.get()
        assert False, f"Could not resolve data type: {data_type}"

class LlvmType(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass
    @abstractmethod
    def get_value(self) -> str:
        pass
    def is_name(self) -> bool:
        return False
    def is_integer(self) -> bool:
        return False

@dataclass(frozen=True)
class LlvmName(LlvmType):
    """
    Example %0, %a, %x.coerce
    """
    name: str
    def _to_string(self) -> str:
        return self.name.replace("%", "").replace(".", "_")
    def get_name(self) -> str:
        return self._to_string()
    def get_value(self) -> str:
        return self._to_string()
    def is_name(self) -> bool:
        return True

@dataclass(frozen=True)
class LlvmInteger(LlvmType):
    value: int
    def get_name(self) -> str:
        return str(self.value)
    def get_value(self) -> str:
        return f'x"{self.value:x}"'
    def is_integer(self) -> bool:
        return True

class LlvmTypeFactory:
    text: str
    def __init__(self, text: str):
        self.text = text
        self._msg = Messages()
    def resolve(self) -> LlvmType:
        self._msg.function_start("resolve", False)
        if "%" in self.text:
            return LlvmName(self.text)
        with contextlib.suppress(ValueError):
            value = int(self.text)
            return LlvmInteger(value)
        raise ValueError(f"Unknown LlvmType = {self.text}")

class VectorDeclaration(TypeDeclaration):
    
    data_width: Optional[str]

    def __init__(self, data_width: Optional[str] = None) -> None:
        self.data_width = data_width

    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return (1, self.data_width)

class BooleanDeclaration(TypeDeclaration):
    
    def get_dimensions(self) -> Tuple[int, str]:
        return (1, "1")

    def is_boolean(self) -> bool:
        return True
