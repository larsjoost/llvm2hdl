import contextlib
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from dataclasses import dataclass

from messages import Messages

class TypeDeclaration(ABC):
    
    data_type: str

    @abstractmethod
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
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

    def get_data_width(self) -> str:
        pass

    def is_void(self) -> bool:
        return self.data_type == "void"

class LlvmDeclaration(TypeDeclaration):
    """
    data_type is one of void, i1, i32, i64, i32*, float, 3 x i32 
    """
    def __init__(self, data_type: str) -> None:
        self.data_type = data_type
    
    def _get_pointer_data_width(self) -> str:
        return "32"

    def _get_data_width(self, data_type: str) -> str:
        Messages().function_start(f"data_type={data_type}")
        if self.is_void():
            return "0"
        if "*" in data_type:
            return self._get_pointer_data_width()
        x = data_type.strip()
        x = x.replace("*", "")
        if x[0] == "i":
            return x[1:]
        data_types = {'float': "32"}
        if x in data_types:
            return data_types[x]
        Messages().function_end(x)
        return x

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
            data_width = f"{str(x)}*{data_width}"
        return data_width

    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self) -> str:
        return str(vars(self))

class LlvmPointerDeclaration(TypeDeclaration):
    """
    data_type is one of void, i1, i32, i64, i32*, float, 3 x i32 
    """
    def __init__(self, data_type: str) -> None:
        self.data_type = data_type
    
    def _get_pointer_data_width(self) -> str:
        return "32"

    def _get_data_width(self, data_type: str) -> str:
        return self._get_pointer_data_width()

    def is_pointer(self) -> bool:
        return True
    
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
            data_width = f"{str(x)}*{data_width}"
        return data_width

    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self) -> str:
        return str(vars(self))


class LlvmArrayDeclaration(TypeDeclaration):
    
    index : str

    def __init__(self, data_type: str, index: str):
        self.data_type = data_type
        self.index = index

    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return LlvmDeclaration(self.data_type).get_dimensions()

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

    def get_data_width(self) -> str:
        return LlvmDeclaration(self.data_type).get_data_width()

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
