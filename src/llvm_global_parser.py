from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from bracket_tokenizer import BracketTokenizer, TextToken, Token
from instantiation_point import InstantiationPoint
from llvm_constant import ClassDeclaration, Constant, GlobalVariableDeclaration, DeclarationContainer, ReferenceDeclaration
from llvm_source_file import LlvmSourceLine

from llvm_type import LlvmConstantName, LlvmReferenceName, LlvmVariableName
from llvm_declarations import LlvmDeclarationFactory, LlvmIntegerDeclarationFactory, LlvmListDeclarationFactory

@dataclass
class LlvmGlobalType:
    definition: str
    initialization: str

class LlvmGlobalTypeParser:

    def _remove_comma_section(self, tokens: List[Token]) -> List[Token]:
        result : List[Token] = []
        for i in tokens:
            if i.contains_comma():
                last_part = i.remove_everything_after_comma()
                if last_part is not None:
                    result.append(TextToken(content=last_part))
                return result
            result.append(i)
        return result

    def _remove_empty_element(self, tokens: List[Token]) -> List[Token]:
        return [i for i in tokens if not i.is_empty()]

    def _split_by_space(self, tokens: List[Token]) -> List[Token]:
        result: List[Token] = []
        for i in tokens:
            if i.is_split_allowed():
                result.extend(TextToken(content=x) for x in i.split(" "))
            else:
                result.append(i)
        return result  

    def parse(self, source: str) -> LlvmGlobalType:
        """
        private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
        """
        parsed_definition = BracketTokenizer().tokenize(source)
        first_part = self._remove_comma_section(tokens=parsed_definition)
        clean_first_part = self._remove_empty_element(tokens=first_part)
        split_by_space = self._split_by_space(tokens=clean_first_part)
        type_definition = split_by_space[-2].get_content().strip()
        initialization = split_by_space[-1].get_content().strip()
        return LlvmGlobalType(definition=type_definition, initialization=initialization)

class LlvmGlobalParserBase(ABC):

    def _parse_initialization_element(self, initialization: str) -> Constant:
        """
        initialization: 
        i32 23
        10
        """
        x = initialization.split()
        one_element = len(x) == 1
        value = x[0] if one_element else x[1]
        data_type = None if one_element else LlvmIntegerDeclarationFactory(data_type=x[0]).get()
        return Constant(value=value, data_type=data_type)

    def _parse_initialization(self, initialization: str) -> List[Constant]:
        definitions: List[Constant] = [
            self._parse_initialization_element(initialization=i)
            for i in initialization.split(",")
        ]
        return definitions

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
        return DeclarationContainer(declaration=class_declaration)

    def match(self, source: List[str]) -> bool:
        return "type" in source
        
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
        return DeclarationContainer(declaration=reference_declaration)

    def match(self, source: List[str]) -> bool:
        return "alias" in source
        
class LlvmGlobalVariableParser(LlvmGlobalParserBase):
    
    def parse(self, name: str, source: str, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        From https://llvm.org/docs/LangRef.html :
        
        @<GlobalVarName> = [Linkage] [PreemptionSpecifier] [Visibility]
                   [DLLStorageClass] [ThreadLocal]
                   [(unnamed_addr|local_unnamed_addr)] [AddrSpace]
                   [ExternallyInitialized]
                   <global | constant> <Type> [<InitializerConstant>]
                   [, section "name"] [, partition "name"]
                   [, comdat [($name)]] [, align <Alignment>]
                   [, no_sanitize_address] [, no_sanitize_hwaddress]
                   [, sanitize_address_dyninit] [, sanitize_memtag]
                   (, !name !N)*
        
        name = source
        @_ZZ3firfE6buffer = internal unnamed_addr global [4 x float] zeroinitializer, align 16
        @_ZZ4mainE1a = internal global i32 0, align 4
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
        @_ZZ4mainE1a = internal global i32 0, align 4
        """
        global_type = LlvmGlobalTypeParser().parse(source=source)
        data_type = LlvmDeclarationFactory().get(data_type=global_type.definition)
        initialization = self._parse_initialization(initialization=global_type.initialization)
        declaration = GlobalVariableDeclaration(instruction=instruction, 
                                                   instantiation_point=InstantiationPoint(), 
                                                   name=LlvmConstantName(name), 
                                                   type=data_type, 
                                                   values=initialization)
        return DeclarationContainer(declaration=declaration)

    def match(self, source: List[str]) -> bool:
        return "constant" in source or "global" in source
        
class LlvmGlobalParser:
    
    def parse(self, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        Examples:
                   
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i3}2 3], align 4
        @_ZN9ClassTestC1Eii = dso_local unnamed_addr alias void (%class.ClassTest*, i32, i32), void (%class.ClassTest*, i32, i32)* @_ZN9ClassTestC2Eii
        %class.ClassTest = type { i32, i32 }
        @_ZZ3firfE6buffer = internal unnamed_addr global [4 x float] zeroinitializer, align 16
        @_ZZ4mainE1a = internal global i32 0, align 4
        """
        assignment = instruction.line.split("=")
        name = assignment[0].strip()    
        source = assignment[1].strip()
        for i in [LlvmGlobalClassParser(), LlvmGlobalVariableParser(), LlvmGlobalReferenceParser()]:
            if i.match(source.split()):
                return i.parse(name=name, source=source, instruction=instruction)
        assert False, f"Could not parse instruction {instruction}"

