

from abc import ABC, abstractmethod
import contextlib
from dataclasses import dataclass

from messages import Messages

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
        if "%" in self.text:
            return LlvmName(self.text)
        with contextlib.suppress(ValueError):
            value = int(self.text)
            return LlvmInteger(value)
        raise ValueError(f"Unknown LlvmType = {self.text}")
