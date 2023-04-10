from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from llvm_type import LlvmBoolean, LlvmConstantName, LlvmFloat, LlvmHex, LlvmInteger, LlvmPointer, \
    LlvmType, LlvmVariableName

class VhdlType(ABC):
    @abstractmethod
    def get_value(self) -> str:
        pass
    @abstractmethod
    def get_name(self) -> str:
        pass
    def is_name(self) -> bool:
        return False
    def is_integer(self) -> bool:
        return False
    def get_data_width(self) -> Optional[int]:
        return None

class VhdlTypeMatch(ABC):
    @abstractmethod
    def match(self, llvm_type: LlvmType) -> bool:
        pass
    @abstractmethod
    def get(self, llvm_type: LlvmType) -> VhdlType:
        pass

@dataclass(frozen=True)
class VhdlName:
    name: str

class VhdlVariableName(VhdlName, VhdlType):
    """
    Example %0, %a, %x.coerce
    """
    def get_name(self) -> str:
        return f"var_{self.name}"
    def get_value(self) -> str:
        return self.name
    def is_name(self) -> bool:
        return True

class VhdlVariableNameMatch(VhdlTypeMatch):
    def match(self, llvm_type: LlvmType) -> bool:
        return llvm_type.is_variable()
    def get(self, llvm_type: LlvmType) -> VhdlType:
        return VhdlVariableName(name=llvm_type.translate_name())

class VhdlConstantName(VhdlName, VhdlType):
    """
    Example @__const_main_n.n
    """
    def get_name(self) -> str:
        return self.name
    def get_value(self) -> str:
        return self.name
    def is_name(self) -> bool:
        return True

class VhdlConstantNameMatch(VhdlTypeMatch):
    def match(self, llvm_type: LlvmType) -> bool:
        return isinstance(llvm_type, LlvmConstantName)
    def get(self, llvm_type: LlvmType) -> VhdlType:
        return VhdlConstantName(name=llvm_type.translate_name())

class VhdlReferenceName(VhdlName, VhdlType):
    """
    Example @__const_main_n.n
    """
    def get_name(self) -> str:
        return self.name
    def get_value(self) -> str:
        return self.name
    def is_name(self) -> bool:
        return True

def number_to_name(number: str) -> str:
    return number.replace(".", "_").replace("-", "minus_") 
    
@dataclass(frozen=True)
class VhdlInteger(VhdlType):
    value: int
    def get_name(self) -> str:
        vhdl_name = number_to_name(str(self.value)) 
        return f"integer_{vhdl_name}"
    def get_value(self) -> str:
        return f'x"{self.value:x}"'
    def is_integer(self) -> bool:
        return True
    
class VhdlIntegerMatch(VhdlTypeMatch):
    def match(self, llvm_type: LlvmType) -> bool:
        return isinstance(llvm_type, LlvmInteger)
    def get(self, llvm_type: LlvmType) -> VhdlType:
        return VhdlInteger(value=int(llvm_type.translate_name()))

@dataclass(frozen=True)
class VhdlFloat(VhdlType):
    value: float
    def get_name(self) -> str:
        vhdl_name = number_to_name(str(self.value)) 
        return f"float_{vhdl_name}"
    def get_value(self) -> str:
        return f'{self.value}'
    
class VhdlFloatMatch(VhdlTypeMatch):
    def match(self, llvm_type: LlvmType) -> bool:
        return isinstance(llvm_type, LlvmFloat)
    def get(self, llvm_type: LlvmType) -> VhdlType:
        return VhdlFloat(value=float(llvm_type.translate_name()))

@dataclass(frozen=True)
class VhdlHex(VhdlType):
    value: str
    def get_name(self) -> str:
        return f"hex_{self.value}"
    def get_value(self) -> str:
        return f'to_real(x"{self.value}")'
    def get_data_width(self) -> Optional[int]:
        return len(self.value) * 4
    
class VhdlHexMatch(VhdlTypeMatch):
    def match(self, llvm_type: LlvmType) -> bool:
        return isinstance(llvm_type, LlvmHex)
    def get(self, llvm_type: LlvmType) -> VhdlType:
        return VhdlHex(value=llvm_type.translate_name())

@dataclass(frozen=True)
class VhdlPointer(VhdlType):
    value: str
    offset: int
    def get_name(self) -> str:
        return f"{self.value}({self.offset})"
    def get_value(self) -> str:
        return f"{self.value}({self.offset})"
    def get_data_width(self) -> Optional[int]:
        return 32
    
class VhdlPointerMatch(VhdlTypeMatch):
    def match(self, llvm_type: LlvmType) -> bool:
        return isinstance(llvm_type, LlvmPointer)
    def get(self, llvm_type: LlvmType) -> VhdlType:
        offset = llvm_type.get_offset()
        assert offset is not None
        return VhdlPointer(value=llvm_type.translate_name(), offset=offset)

@dataclass(frozen=True)
class VhdlBoolean(VhdlType):
    value: str
    def get_name(self) -> str:
        return self.value
    def get_value(self) -> str:
        return self.value
    
class VhdlBooleanMatch(VhdlTypeMatch):
    def match(self, llvm_type: LlvmType) -> bool:
        return isinstance(llvm_type, LlvmBoolean)
    def get(self, llvm_type: LlvmType) -> VhdlType:
        return VhdlBoolean(value=llvm_type.translate_name())

class VhdlTypeFactory:
    llvm_type: LlvmType
    def __init__(self, llvm_type: LlvmType):
        self.llvm_type = llvm_type
    def resolve(self) -> VhdlType:
        types = [VhdlVariableNameMatch(), VhdlConstantNameMatch(), VhdlIntegerMatch(), 
                 VhdlFloatMatch(), VhdlHexMatch(), VhdlPointerMatch(), VhdlBooleanMatch()]
        for i in types:
            if i.match(llvm_type=self.llvm_type):
                return i.get(llvm_type=self.llvm_type)
        raise ValueError(f"Unknown LlvmType = {self.llvm_type}")
