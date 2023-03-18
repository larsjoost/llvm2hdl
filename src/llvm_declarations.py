
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass
from llvm_constant_container import ConstantContainer
from llvm_type import LlvmPointer, LlvmType, LlvmTypeFactory, LlvmVariableName
from llvm_type_declaration import TypeDeclaration, TypeDeclarationFactory


from function_logger import log_entry_and_exit

class LlvmVoidDeclaration(TypeDeclaration):

    def get_dimensions(self) -> Tuple[int, str]:
        return 1, self.get_data_width()

    def is_void(self) -> bool:
        return True

    def get_data_width(self) -> str:
        return "1"

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
        assert isinstance(self.data_width, int), \
            f"data_width = {self.data_width} is not an integer"
    
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
        data_type = self.data_type.strip()
        data_width = int(data_type[1:])
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

    def resolve_type(self, data_type: str) -> LlvmType:
        # 1) data_type = "([4 x float], ptr @_ZZ3firfE6buffer, i64 0, i64 1)"
        # 2) data_type = "@_ZZ3firfE6buffer"
        if "," not in data_type:
            return LlvmTypeFactory(data_type).resolve()
        split_data_type = data_type.strip("()").split(",")
        # 1) split_data_type = ["[4 x float], "ptr @_ZZ3firfE6buffer", "i64 0", "i64 1"]
        name = split_data_type[1].split()[-1]
        # name = @_ZZ3firfE6buffer
        offset = int(split_data_type[-1].split()[-1])
        # offset = 1
        return LlvmPointer(name=LlvmVariableName(name=name), offset=offset)

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

class LlvmTypeResolver:
    def get(self, data_type: str, declaration_types: List[TypeDeclarationFactory]) -> TypeDeclaration:
        for i in declaration_types:
            if i.match():
                return i.get()
        assert False, f"Could not resolve data type: {data_type}"

@dataclass
class LlvmArrayDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str
    
    def match(self) -> bool:
        return " x " in self.data_type

    def _parse_data_type(self, data_type: str) -> TypeDeclaration:
        declaration_types = [ 
            LlvmFloatDeclarationFactory(data_type=data_type),
            LlvmIntegerDeclarationFactory(data_type=data_type)
        ]    
        return LlvmTypeResolver().get(data_type=data_type, declaration_types=declaration_types)
    
    def get(self) -> TypeDeclaration:
        x = self.data_type.split(" x ")
        data_type = x[1]
        y = self._parse_data_type(data_type=data_type)
        return LlvmArrayDeclaration(x=LlvmConstantDeclaration(x[0]), y=y)

@dataclass
class LlvmListDeclaration(TypeDeclaration):
    """
    Declaration: <type>, <type>
    Example:
    i32, i32
    """
    data_types: List[TypeDeclaration]

    def get_data_width(self) -> str:
        data_width = [i.get_data_width() for i in self.data_types]        
        return " + ".join(data_width)

    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return 1, self.get_data_width()

@dataclass
class LlvmListDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str

    def match(self) -> bool:
        return "," in self.data_type

    def get(self) -> TypeDeclaration:
        elements = self.data_type.split(",")
        data_types = [
            LlvmIntegerDeclarationFactory(data_type=i).get() for i in elements]
        return LlvmListDeclaration(data_types=data_types)

@dataclass
class LlvmClassDeclaration(TypeDeclaration):
    """
    Declaration: %class.<name>
    Example:
    %class.ClassTest
    """
    name: LlvmVariableName
    constants: ConstantContainer

    def get_data_width(self) -> str:
        data_width = self.constants.get_data_width(name=self.name)        
        assert data_width is not None
        return data_width

    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return 1, self.get_data_width()

@dataclass
class LlvmClassDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str
    constants: Optional[ConstantContainer]

    def match(self) -> bool:
        if self.constants is None:
            return False
        return self.data_type.startswith('%class.')

    def get(self) -> TypeDeclaration:
        assert self.constants is not None
        return LlvmClassDeclaration(name=LlvmVariableName(self.data_type), 
                                    constants=self.constants)

@dataclass
class LlvmVariableDeclaration(TypeDeclaration):
    """
    Declaration: %<name>
    Example:
    %call
    """
    name: LlvmVariableName

    #TODO: Not implemented yet
    def get_data_width(self) -> str:
        return ""

    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return 1, self.get_data_width()

@dataclass
class LlvmVariableDeclarationFactory(TypeDeclarationFactory):
    
    data_type: str
    
    def match(self) -> bool:
        return self.data_type.startswith('%')

    def get(self) -> TypeDeclaration:
        return LlvmVariableDeclaration(name=LlvmVariableName(self.data_type))

class LlvmDeclarationFactory:

    def get(self, data_type: str, 
            constants: Optional[ConstantContainer] = None) -> TypeDeclaration:
        declaration_types = [
            LlvmVoidDeclarationFactory(data_type=data_type),
            LlvmFloatDeclarationFactory(data_type=data_type),
            LlvmPointerDeclarationFactory(data_type=data_type),
            LlvmIntegerDeclarationFactory(data_type=data_type),
            LlvmArrayDeclarationFactory(data_type=data_type),
            LlvmClassDeclarationFactory(data_type=data_type, constants=constants),
            LlvmVariableDeclarationFactory(data_type=data_type)
        ]    
        return LlvmTypeResolver().get(data_type=data_type, declaration_types=declaration_types)

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
