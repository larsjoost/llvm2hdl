from abc import ABC, abstractmethod
from typing import List
from instantiation_point import InstantiationPoint
from llvm_constant import ClassDeclaration, Constant, ConstantDeclaration, DeclarationContainer, GlobalVariableDeclaration, ReferenceDeclaration
from llvm_source_file import LlvmSourceLine

from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmConstantName, LlvmReferenceName, LlvmVariableName
from llvm_declarations import LlvmArrayDeclarationFactory, LlvmIntegerDeclarationFactory, LlvmListDeclarationFactory

class LlvmGlobalParserBase(ABC):

    def _parse_definition(self, definition: str) -> List[Constant]:
        definitions: List[Constant] = []
        for i in definition.split(","):
            x = i.split()
            data_type = LlvmIntegerDeclarationFactory(data_type=x[0]).get()
            value = x[1]
            definitions.append(Constant(value=value, data_type=data_type))
        return definitions

    def _get_array_data_type(self, source: str) -> TypeDeclaration:
        """
        private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
        """
        source_split = source.split("[")
        # source_split = ["private unnamed_addr constant ","3 x i32]", "i32 1, i32 2, i32 3], align 4"]
        data_type = source_split[1].split("]")[0]
        # data_type = "3 x i32"
        return LlvmArrayDeclarationFactory(data_type=data_type).get()
        
    @abstractmethod
    def parse(self, name: str, source: str, instruction: LlvmSourceLine) -> DeclarationContainer:
        pass

    @abstractmethod
    def match(self, source: List[str]   ) -> bool:
        pass

class LlvmGlobalClassParser(LlvmGlobalParserBase):
    
    def parse(self, name: str, source: str, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        %class.ClassTest = type { i32, i32 }
        """
        source_split = source.split("{")
        # source_split = ["%class.ClassTest = type ","i32, i32 }"]
        data_type = source_split[-1].split("}")[0]
        # data_type = "i32, i32"
        declaration = LlvmListDeclarationFactory(data_type=data_type).get()
        class_declaration = ClassDeclaration(instruction=instruction, instantiation_point=InstantiationPoint(), 
                                             name=LlvmVariableName(name), type=declaration)
        return DeclarationContainer(instruction=instruction, declaration=class_declaration)

    def match(self, source: List[str]) -> bool:
        return "type" in source
        
class LlvmGlobalConstantParser(LlvmGlobalParserBase):
    
    def parse(self, name: str, source: str, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
        """
        source_split = source.split("[")
        # source_split = ["private unnamed_addr constant ","3 x i32]", "i32 1, i32 2, i32 3], align 4"]
        definition = source_split[-1].split("]")[0]
        # definition = "i32 1, i32 2, i32 3"
        constant_type = self._get_array_data_type(source=source)
        definitions = self._parse_definition(definition=definition)
        constant_declaration = ConstantDeclaration(instruction=instruction, 
                                                   instantiation_point=InstantiationPoint(), 
                                                   name=LlvmConstantName(name), 
                                                   type=constant_type, 
                                                   values=definitions)
        return DeclarationContainer(instruction=instruction, declaration=constant_declaration)

    def match(self, source: List[str]) -> bool:
        return "constant" in source
        
class LlvmGlobalReferenceParser(LlvmGlobalParserBase):

    def parse(self, name: str, source: str, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        @_ZN9ClassTestC1Eii = dso_local unnamed_addr alias void (%class.ClassTest*, i32, i32), void (%class.ClassTest*, i32, i32)* @_ZN9ClassTestC2Eii
        """
        reference = source.split()[-1]
        reference_declaration = ReferenceDeclaration(instruction=instruction, 
                                                     instantiation_point=InstantiationPoint(),
                                                     name=LlvmReferenceName(name), 
                                                     reference=LlvmReferenceName(reference))
        return DeclarationContainer(instruction=instruction, declaration=reference_declaration)

    def match(self, source: List[str]) -> bool:
        return "alias" in source
        

class LlvmGlobalVariableParser(LlvmGlobalParserBase):

    def parse(self, name: str, source: str, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        @_ZZ3firfE6buffer = internal unnamed_addr global [4 x float] zeroinitializer, align 16
        """
        data_type = self._get_array_data_type(source=source)
        declaration = GlobalVariableDeclaration(instruction=instruction, 
                                                          instantiation_point=InstantiationPoint(),
                                                          name=LlvmVariableName(name),
                                                          type=data_type)
        return DeclarationContainer(instruction=instruction, declaration=declaration)

    def match(self, source: List[str]) -> bool:
        return "global" in source
        

class LlvmGlobalParser:
    
    def parse(self, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i3}2 3], align 4
        @_ZN9ClassTestC1Eii = dso_local unnamed_addr alias void (%class.ClassTest*, i32, i32), void (%class.ClassTest*, i32, i32)* @_ZN9ClassTestC2Eii
        %class.ClassTest = type { i32, i32 }
        @_ZZ3firfE6buffer = internal unnamed_addr global [4 x float] zeroinitializer, align 16
        """
        assignment = instruction.line.split("=")
        name = assignment[0].strip()    
        source = assignment[1].strip()
        for i in [LlvmGlobalClassParser(), LlvmGlobalConstantParser(), LlvmGlobalReferenceParser(), LlvmGlobalVariableParser()]:
            if i.match(source.split()):
                return i.parse(name=name, source=source, instruction=instruction)
        assert False, f"Could not parse instruction {instruction}"

