from abc import ABC, abstractmethod
from dataclasses import dataclass
from llvm_type import LlvmConstantName, LlvmFloat, LlvmHex, LlvmInteger, \
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
        return self.name
    def get_value(self) -> str:
        return self.name
    def is_name(self) -> bool:
        return True

class VhdlVariableNameMatch(VhdlTypeMatch):
    def match(self, llvm_type: LlvmType) -> bool:
        return isinstance(llvm_type, LlvmVariableName)
    def get(self, llvm_type: LlvmType) -> VhdlType:
        return VhdlVariableName(name=llvm_type.get_name())

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
        return VhdlConstantName(name=llvm_type.get_name())

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
        return VhdlInteger(value=int(llvm_type.get_name()))

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
        return VhdlFloat(value=float(llvm_type.get_name()))

@dataclass(frozen=True)
class VhdlHex(VhdlType):
    value: str
    def get_name(self) -> str:
        return f"hex_{self.value}"
    def get_value(self) -> str:
        return f'x"{self.value}"'
    
class VhdlHexMatch(VhdlTypeMatch):
    def match(self, llvm_type: LlvmType) -> bool:
        return isinstance(llvm_type, LlvmHex)
    def get(self, llvm_type: LlvmType) -> VhdlType:
        return VhdlHex(value=llvm_type.get_name())

class VhdlTypeFactory:
    llvm_type: LlvmType
    def __init__(self, llvm_type: LlvmType):
        self.llvm_type = llvm_type
    def resolve(self) -> VhdlType:
        types = [VhdlVariableNameMatch(), VhdlConstantNameMatch(), VhdlIntegerMatch(), 
                 VhdlFloatMatch(), VhdlHexMatch()]
        for i in types:
            if i.match(llvm_type=self.llvm_type):
                return i.get(llvm_type=self.llvm_type)
        raise ValueError(f"Unknown LlvmType = {self.llvm_type}")
