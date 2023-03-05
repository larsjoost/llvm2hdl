from abc import ABC, abstractmethod
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

class LlvmTypeMatch(ABC):
    @abstractmethod
    def match(self, text: str) -> bool:
        pass
    @abstractmethod
    def get(self, text: str) -> LlvmType:
        pass

@dataclass(frozen=True)
class LlvmName:
    name: str

class LlvmVariableName(LlvmName, LlvmType):
    """
    Example %0, %a, %x.coerce
    """
    def _to_string(self) -> str:
        return self.name.replace("%", "").replace(".", "_")
    def get_name(self) -> str:
        return self._to_string()
    def get_value(self) -> str:
        return self._to_string()
    def is_name(self) -> bool:
        return True
    def equals(self, other: LlvmName) -> bool:
        return self.name == other.name

class LlvmVariableNameMatch(LlvmTypeMatch):
    def match(self, text: str) -> bool:
        return text.startswith("%")
    def get(self, text: str) -> LlvmType:
        return LlvmVariableName(name=text)

class LlvmConstantName(LlvmName, LlvmType):
    """
    Example @__const_main_n.n
    """
    def _to_string(self) -> str:
        return self.name.split(".")[-1]
    def get_name(self) -> str:
        return self._to_string()
    def get_value(self) -> str:
        return self._to_string()
    def is_name(self) -> bool:
        return True
    def match(self) -> bool:
        return self.name.startswith("@")

class LlvmConstantNameMatch(LlvmTypeMatch):
    def match(self, text: str) -> bool:
        return text.startswith("@")
    def get(self, text: str) -> LlvmType:
        return LlvmConstantName(name=text)

class LlvmReferenceName(LlvmName, LlvmType):
    """
    Example @__const_main_n.n
    """
    def _to_string(self) -> str:
        return self.name.split(".")[-1]
    def get_name(self) -> str:
        return self._to_string()
    def get_value(self) -> str:
        return self._to_string()
    def is_name(self) -> bool:
        return True
    def match(self) -> bool:
        return self.name.startswith("@")

@dataclass(frozen=True)
class LlvmInteger(LlvmType):
    value: int
    def get_name(self) -> str:
        return str(self.value)
    def get_value(self) -> str:
        return f'x"{self.value:x}"'
    def is_integer(self) -> bool:
        return True
    
class LlvmIntegerMatch(LlvmTypeMatch):
    def match(self, text: str) -> bool:
        return text.isdigit()
    def get(self, text: str) -> LlvmType:
        return LlvmInteger(value=int(text))

@dataclass(frozen=True)
class LlvmFloat(LlvmType):
    value: float
    def get_name(self) -> str:
        return str(self.value)
    def get_value(self) -> str:
        return f'{self.value}'
    
class LlvmFloatMatch(LlvmTypeMatch):
    def match(self, text: str) -> bool:
        try:
            float(text)
        except ValueError:
            return False
        return True
    def get(self, text: str) -> LlvmType:
        return LlvmFloat(value=float(text))

@dataclass(frozen=True)
class LlvmHex(LlvmType):
    value: str
    def get_name(self) -> str:
        return self.value
    def get_value(self) -> str:
        return f'x"{self.value}"'
    
class LlvmHexMatch(LlvmTypeMatch):
    def match(self, text: str) -> bool:
        return text.startswith("0x")
    def get(self, text: str) -> LlvmType:
        return LlvmHex(value=text[2:])

class LlvmTypeFactory:
    text: str
    def __init__(self, text: str):
        self.text = text
        self._msg = Messages()
    def resolve(self) -> LlvmType:
        types = [LlvmVariableNameMatch(), LlvmConstantNameMatch(), LlvmIntegerMatch(), LlvmFloatMatch(), LlvmHexMatch()]
        for i in types:
            if i.match(text=self.text):
                return i.get(text=self.text)
        raise ValueError(f"Unknown LlvmType = {self.text}")
