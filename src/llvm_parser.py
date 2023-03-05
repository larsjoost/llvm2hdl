from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Union
from instruction import AllocaInstruction, BitcastInstruction, CallInstruction, GetelementptrInstruction, DefaultInstruction, ReturnInstruction
from instruction_interface import InstructionArgument, InstructionInterface, LlvmOutputPort, MemoryInterface
from llvm_constant import ClassDeclaration, Constant, ConstantDeclaration, DeclarationContainer, ReferenceDeclaration
from llvm_constant_container import ConstantContainer
from llvm_function import LlvmFunction, LlvmFunctionContainer
from llvm_instruction import LlvmInstruction
from llvm_module import LlvmModule
from llvm_source_file import LlvmSourceConstants, LlvmSourceFile, LlvmSourceFileParser, LlvmSourceFunction, LlvmSourceFunctions, LlvmSourceLine

from messages import Messages
from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmConstantName, LlvmReferenceName, LlvmVariableName, LlvmTypeFactory
from llvm_declarations import LlvmArrayDeclarationFactory, LlvmDeclarationFactory, LlvmIntegerDeclarationFactory, LlvmListDeclarationFactory, LlvmPointerDeclaration, LlvmIntegerDeclaration

from function_logger import log_entry_and_exit

@dataclass
class InstructionPosition:
    opcode: int
    operands: List[Tuple[int, int]]
    data_type: int
    sub_type : Optional[int] = None
    
class InstructionPositionParser:
    source : List[str]
    opcode : str
    sub_type: Optional[str]
    operands : List[InstructionArgument]
    data_type : str
    def __init__(self, instruction: List[str], position: InstructionPosition):
        self.source = instruction
        self.opcode = instruction[position.opcode]
        self.sub_type = instruction[position.sub_type] if position.sub_type is not None else None
        self.data_type = instruction[position.data_type].replace(",", "")
        self.operands = [self._parse_operand(instruction, item, index) for index, item in enumerate(position.operands)]
    def _parse_operand(self, instruction: List[str], item: Tuple[int, int], index: int) -> InstructionArgument:
        type_index, value_index = item
        value = instruction[value_index]
        signal_name = LlvmTypeFactory(value.replace(",","")).resolve()
        port_name = chr(ord('a') + index)
        data_type = LlvmDeclarationFactory().get(instruction[type_index].replace(",", ""))
        return InstructionArgument(port_name=port_name, signal_name=signal_name, data_type=data_type)
    def __str__(self) -> str:
        return str(vars(self))

class LlvmParserException(Exception):
    pass

class LlvmParserUtilities:

    def __init__(self):
        self._msg = Messages()

    def _remove_empty_elements(self, x: List[str]) -> List[str]:
        return [i for i in x if len(i) > 0]

    def _split(self, x: str, split_char: str) -> List[str]:
        return self._remove_empty_elements(x.split(split_char))

    def split_equal_sign(self, x: str) -> List[str]:
        return self._split(x, '=')

    def split_space(self, x: str) -> List[str]:
        return self._split(x, ' ')

    def split_comma(self, x: str) -> List[str]:
        return self._split(x, ',')

    def get_list_element(self, x : Union[List[str], Tuple[str, str, str]], index : int) -> str:
        return x[index].strip()

    def remove_first_word(self, text : str) -> str:
        return text.strip().partition(' ')[2]

    def first_word(self, text: str) -> str:
        return text.split()[0]

@dataclass
class LlvmInstructionLabel(LlvmInstruction):
    name: str
    def is_valid(self) -> bool:
        return False
    
@dataclass
class LlvmInstructionCommand(LlvmInstruction):
    destination: Optional[LlvmVariableName]
    instruction: InstructionInterface
    def is_valid(self) -> bool:
        return self.instruction.is_valid()
    def get_destination(self) -> Optional[LlvmVariableName]:
        return self.destination
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return self.instruction.get_output_port()
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.instruction.get_operands()
    def get_data_type(self) -> Optional[TypeDeclaration]:
        return self.instruction.get_data_type()
    def get_library(self) -> str:
        return self.instruction.get_library()
    def get_instance_name(self) -> str:
        return self.instruction.get_instance_name()
    def get_generic_map(self) -> Optional[List[str]]:
        return self.instruction.get_generic_map()
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return self.instruction.get_memory_interface()
    def is_memory(self) -> bool:
        return self.instruction.is_memory()
    def map_function_arguments(self) -> bool:
        return self.instruction.map_function_arguments()
    
class LlvmInstructionLabelParser:

    def parse(self, source_line: LlvmSourceLine) -> LlvmInstructionLabel:
        """
        entry:
        """
        name = source_line.line.split(":")[0]
        return LlvmInstructionLabel(name=name, source_line=source_line)

@dataclass
class InstructionParserArguments:
    instruction: str
    destination: Optional[LlvmVariableName]
    constants: ConstantContainer

class InstructionParser(ABC):

    def __init__(self):
        self._msg = Messages()

    @abstractmethod
    def parse(self, arguments: InstructionParserArguments) -> Optional[InstructionInterface]:
        pass

class BitCastInstructionParser(InstructionParser):

    def parse(self, arguments: InstructionParserArguments) -> InstructionInterface:
        utils = LlvmParserUtilities()
        c = utils.split_space(arguments.instruction)
        opcode = c[0]
        data_width = int(" ".join(c[1:-3]))
        data_type = LlvmIntegerDeclaration(data_width=data_width)
        signal_name = LlvmVariableName(c[-3])
        argument = InstructionArgument(signal_name=signal_name, data_type=data_type)
        operands = [argument]
        return BitcastInstruction(
            opcode=opcode, data_type=data_type, operands=operands
        )

class GetelementptrInstructionParser(InstructionParser):

    def parse(self, arguments: InstructionParserArguments) -> InstructionInterface:
        """
        1) instruction = "getelementptr inbounds i32, ptr %a, i64 1"
        2) instruction = "getelementptr inbounds [4 x i32], ptr %n, i64 0, i64 1"
        """
        opcode = arguments.instruction.split()[0]
        utils = LlvmParserUtilities()
        c = utils.split_comma(arguments.instruction)
        # 1) c = "getelementptr inbounds i32" , "ptr %a", "i64 1"
        # 2) c = "getelementptr inbounds [4 x i32]", "ptr %n", "i64 0", "i64 1"
        data_type: List[str] = c[1].rsplit(maxsplit=1)
        # 1) data_type = "ptr", "%a"
        # 2) data_type = "ptr", "%n"
        array_index : List[str] = c[-1].rsplit(maxsplit=1)
        # 1) array_index = "i64", "1"
        # 2) array_index = "i64", "0"
        pointer_offset = int(array_index[-1])
        signal_data_type = LlvmPointerDeclaration()
        signal_name = LlvmVariableName(data_type[1])
        argument = InstructionArgument(signal_name=signal_name, data_type=signal_data_type)
        operands = [argument]
        return GetelementptrInstruction(opcode=opcode, data_type=signal_data_type, operands=operands, offset=pointer_offset)
        
class ReturnInstructionParser(InstructionParser):

    def parse(self, arguments: InstructionParserArguments) -> InstructionInterface:
        """
        instruction is expected to be one of:
            "ret i32 %add"
            "ret void"
        """
        utils = LlvmParserUtilities()
        a = utils.split_space(arguments.instruction)
        opcode = a[0]
        data_width = int(a[1].strip())
        data_type = LlvmIntegerDeclaration(data_width=data_width)
        try:
            signal_name = LlvmVariableName(a[2].strip())
            argument = InstructionArgument(signal_name=signal_name, data_type=data_type)
            operands = [argument]
        except IndexError:
            operands = []
        return ReturnInstruction(opcode=opcode, data_type=data_type, operands=operands)

class AllocaInstructionParser(InstructionParser):

    def parse(self, arguments: InstructionParserArguments) -> InstructionInterface:
        # alloca [3 x i32], align 4
        # alloca i32, align 4
        # alloca %class.ClassTest, align 4
        x = arguments.instruction.split(",")
        y = x[0].split(maxsplit=1)
        opcode = y[0]
        data_type_position = y[1].replace("[", "").replace("]", "")
        data_type = LlvmDeclarationFactory().get(data_type=data_type_position, constants=arguments.constants)
        initialization = arguments.constants.get_initialization(name=arguments.destination)
        return AllocaInstruction(
            opcode=opcode, data_type=data_type, output_port_name=arguments.destination, initialization=initialization
        )

class CallInstructionParser(InstructionParser):

    def _split_function_call_from_arguments(self, text: str) -> Tuple[str, str]:
        split_text = text.split('(', maxsplit=1)
        function_call = split_text[0]
        arguments = split_text[1].rsplit(')', maxsplit=1)[0]
        return function_call, arguments

    def _is_ignored_function_call(self, name: str) -> bool:
        ignored_functions = ["@llvm.lifetime", "@llvm.memcpy"]
        return any(name.startswith(i) for i in ignored_functions)

    def _get_call_instruction(self, function_name: str, llvm_function: bool, return_type: str, arguments: str) -> CallInstruction:
        data_type = LlvmDeclarationFactory().get(return_type)
        operands = LlvmArgumentParser().parse(arguments=arguments, unnamed=True)
        return CallInstruction(opcode=function_name, llvm_function=llvm_function, data_type=data_type, operands=operands)

    def _split_function_call(self, function_call: str) -> Tuple[str, str]:
        head_split = function_call.split()
        function_name = head_split[-1]
        return_type = head_split[-2]
        return function_name, return_type

    def parse(self,  arguments: InstructionParserArguments) -> Optional[InstructionInterface]:
        """
        instruction is expected to be one of: 
            "call i32 @_Z3addii(i32 2, i32 3)"
            "tail call i32 @_Z3addii(i32 2, i32 3)"
            "tail call float @llvm.fabs.f32(float %sub.i)"
        """
        function_call, function_arguments = self._split_function_call_from_arguments(text=arguments.instruction)
        # 1) head = "call i32 @_Z3addii"
        # 2) head = "tail call i32 @_Z3addii"
        # tail = "i32 2, i32 3"

        function_name, return_type = self._split_function_call(function_call=function_call)
        llvm_function = function_name.startswith("@llvm.")
        if self._is_ignored_function_call(name=function_name):
            return None
        function_name = function_name.replace(".", "_")
        return self._get_call_instruction(function_name=function_name, llvm_function=llvm_function, return_type=return_type, arguments=function_arguments)

class DefaultInstructionParser(InstructionParser):

    def _get_type_and_two_arguments_instructions(self) -> Dict[str, InstructionPosition]:
        """
        The instruction is expected to be in one of the following formats:
            "fadd float %0, %1"
            "or i1 %cmp, %cmp2"
            "ashr i32 %a, %b" 
        """
        position = InstructionPosition(opcode=0, data_type=1, operands=[(1, 2), (1, 3)]) 
        commands = ["fadd", "fmul", "xor", "and", "or", "ashr", "lshr", "shl"]
        return {i:position for i in commands}

    def _get_arithmetic_instructions(self) -> Dict[str, InstructionPosition]:
        # 1) add nsw i32 %0, %1
        # 2) sub nsw i32 %0, %1
        position = InstructionPosition(opcode=0, data_type=2, operands=[(2, 3), (2, 4)])
        commands = ["add", "sub", "mul"]
        return {i:position for i in commands}

    def _get_special_instructions(self) -> Dict[str, InstructionPosition]:
        """
        The instruction is expected to be in one of the following formats:
            "icmp eq i32 %call, 5"
            "zext i1 %cmp to i32"
            "select i1 %cmp, i32 1, i32 2"
            "trunc i64 %x.coerce to i32"
            "store i32 %a, i32* %a.addr, align 4"
            "load i32, i32* %a.addr, align 4"
            "fcmp ule float %0, %mul.i"
        """
        return {
            "icmp": InstructionPosition(opcode=1, data_type=2, operands=[(2, 3), (2, 4)]),
            "zext": InstructionPosition(opcode=0, data_type=1, operands=[(1, 2)]),
            "trunc": InstructionPosition(opcode=0, data_type=4, operands=[(1, 2)]),
            "select": InstructionPosition(opcode=0, data_type=3, operands=[(1, 2), (3, 4), (5, 6)]),
            "store": InstructionPosition(opcode=0, data_type=1, operands=[(1, 2), (3, 4)]),
            "load": InstructionPosition(opcode=0, data_type=1, operands=[(2, 3)]),
            "fcmp": InstructionPosition(opcode=0, sub_type=1, data_type=2, operands=[(2, 3), (2, 4)])}

    def _get_instruction_positions(self) -> Dict[str, InstructionPosition]:
        dict_1 = self._get_type_and_two_arguments_instructions()
        dict_2 = self._get_arithmetic_instructions()
        dict_3 = self._get_special_instructions()
        return dict_1 | dict_2 | dict_3

    def parse(self,  arguments: InstructionParserArguments) -> InstructionInterface:
        utils = LlvmParserUtilities()
        a = utils.split_space(arguments.instruction)
        position: Dict[str, InstructionPosition] = self._get_instruction_positions()
        opcode = utils.get_list_element(a, 0)
        x = InstructionPositionParser(instruction=a, position=position[opcode])
        data_type = LlvmDeclarationFactory().get(x.data_type)
        return DefaultInstruction(
            opcode=x.opcode,
            sub_type=x.sub_type,
            data_type=data_type,
            operands=x.operands,
            output_port_name="m_tdata"
        )

class LlvmInstructionCommandParser:

    def __init__(self):
        self._msg = Messages()

    def _parse_instruction(self, arguments: InstructionParserArguments) -> Optional[InstructionInterface]:
        parsers: Dict[str, InstructionParser] =  {
            "bitcast": BitCastInstructionParser(),
            "getelementptr": GetelementptrInstructionParser(),
            "ret": ReturnInstructionParser(),
            "alloca": AllocaInstructionParser(),
            "call": CallInstructionParser()}
        instruction_words = arguments.instruction.split()
        parser: InstructionParser = DefaultInstructionParser()
        for i in parsers:
            if i in instruction_words:
                parser = parsers[i]
        return parser.parse(arguments=arguments)

    def parse(self, source_line: LlvmSourceLine, constants: ConstantContainer) -> Optional[LlvmInstructionCommand]:
        """
        1)    %add = add nsw i32 %b, %a
        2)    ret i32 %add
        """
        destination = None
        source = source_line.line
        utils = LlvmParserUtilities()
        if source_line.is_assignment():
            x = source_line.line.split("=")
            destination = LlvmVariableName(utils.get_list_element(x, 0))
            source = utils.get_list_element(x, 1)
        arguments = InstructionParserArguments(instruction=source, destination=destination, constants=constants)
        instruction = self._parse_instruction(arguments=arguments)
        return LlvmInstructionCommand(destination=destination, instruction=instruction, source_line=source_line) if instruction is not None else None

class LlvmArgumentParser:

    def __init__(self) -> None:
        self._msg = Messages()

    def parse(self, arguments: str, unnamed: bool = False) -> List[InstructionArgument]:
        # arguments = "i32 2, i32* nonnull %n"
        # arguments = ptr nocapture noundef readonly %a
        # arguments = ptr noundef nonnull align 4 dereferenceable(8 %a, i32 noundef 1, i32 noundef 2
        result = []
        utils = LlvmParserUtilities()
        for i in utils.split_comma(arguments):
            # 1) i = "i32 2"
            # 2) i = "i32* nonnull %n"
            g = utils.split_space(i) 
            # 1) g = ["i32", "2"]
            # 2) b = ["i32*", "nonnull",  "%n"]
            data_type = LlvmDeclarationFactory().get(data_type=utils.get_list_element(g, 0))
            argument = LlvmTypeFactory(utils.get_list_element(g, -1)).resolve()
            # 1) signal_name = "2"
            # 2) signal_name = "%n"
            result.append(InstructionArgument(signal_name=argument, data_type=data_type, unnamed=unnamed))
        return result

class LlvmInstructionParser:

    def _parse_line(self, line: LlvmSourceLine, constants: ConstantContainer) -> Optional[LlvmInstruction]:
        if line.is_label():
            return LlvmInstructionLabelParser().parse(source_line=line)
        return LlvmInstructionCommandParser().parse(source_line=line, constants=constants)

    def parse(self, lines: List[LlvmSourceLine], constants: ConstantContainer) -> List[LlvmInstruction]:
        """
        entry:
            %add = add nsw i32 %b, %a
            ret i32 %add
        """
        x = [self._parse_line(line=i, constants=constants) for i in lines]
        return [i for i in x if i is not None]

class LlvmFunctionParser:
    
    def __init__(self) -> None:
        self._msg = Messages()

    def _parse_parentesis(self, left_parenthis_split: List[str]) -> Tuple[str, TypeDeclaration]:
        function_definition = left_parenthis_split[0].split()
        function_name = function_definition[-1]
        return_type = LlvmDeclarationFactory().get(function_definition[-2])
        return function_name, return_type

    def _parse_function_description(self, line: str) -> Tuple[str, List[InstructionArgument], TypeDeclaration]:
        """
        1) line = "define dso_local noundef i32 @_Z3addii(i32 noundef %a, i32 noundef %b) local_unnamed_addr #0 {"
        2) line = "define dso_local void @_ZN9ClassTestC2Eii(%class.ClassTest* nocapture noundef nonnull writeonly align 4 dereferenceable(8) %this, i32 noundef %a, i32 noundef %b) unnamed_addr #0 align 2 {"
        3) line = "define dso_local noundef i32 @_Z8for_loopPi(ptr nocapture noundef readonly %a) local_unnamed_addr #0 {"
        """
        left_parenthis_split = line.split("(", maxsplit=1)
        argument_text = left_parenthis_split[1].rsplit(")", maxsplit=1)[0]
        arguments = LlvmArgumentParser().parse(arguments=argument_text)
        function_name, return_type = self._parse_parentesis(left_parenthis_split=left_parenthis_split)
        return function_name, arguments, return_type

    def parse(self, source_function: LlvmSourceFunction, constants: ConstantContainer) -> LlvmFunction:
        """
        define dso_local noundef i32 @_Z3addii(i32 noundef %a, i32 noundef %b) local_unnamed_addr #0 {
        entry:
            %add = add nsw i32 %b, %a
            ret i32 %add
        }
        """
        function_name, arguments, return_type = self._parse_function_description(source_function.lines[0].line)
        comands_excluding_right_bracket = source_function.lines[1:-2]
        instructions = LlvmInstructionParser().parse(lines=comands_excluding_right_bracket, constants=constants)
        return LlvmFunction(name=function_name, arguments=arguments, return_type=return_type, instructions=instructions)

class LlvmConstantParser:
    
    def __init__(self):
        self._msg = Messages()
    
    def _parse_definition(self, definition: str) -> List[Constant]:
        definitions: List[Constant] = []
        for i in definition.split(","):
            x = i.split()
            data_type = LlvmIntegerDeclarationFactory(data_type=x[0]).get()
            value = x[1]
            definitions.append(Constant(value=value, data_type=data_type))
        return definitions

    def _parse_class(self, name: str, source: str, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        %class.ClassTest = type { i32, i32 }
        """
        source_split = source.split("{")
        # source_split = ["%class.ClassTest = type ","i32, i32 }"]
        data_type = source_split[-1].split("}")[0]
        # data_type = "i32, i32"
        declaration = LlvmListDeclarationFactory(data_type=data_type).get()
        return DeclarationContainer(instruction=instruction, class_declaration=ClassDeclaration(name=LlvmVariableName(name), type=declaration))

    def _parse_const(self, name: str, source: str, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
        """
        source_split = source.split("[")
        # source_split = ["private unnamed_addr constant ","3 x i32]", "i32 1, i32 2, i32 3], align 4"]
        definition = source_split[-1].split("]")[0]
        # definition = "i32 1, i32 2, i32 3"
        data_type = source_split[1].split("]")[0]
        # data_type = "3 x i32"
        constant_type = LlvmArrayDeclarationFactory(data_type=data_type).get()
        definitions = self._parse_definition(definition=definition)
        return DeclarationContainer(instruction=instruction, constant_declaration=ConstantDeclaration(name=LlvmConstantName(name), type=constant_type, values=definitions))

    def _parse_reference(self, name: str, source: str, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        @_ZN9ClassTestC1Eii = dso_local unnamed_addr alias void (%class.ClassTest*, i32, i32), void (%class.ClassTest*, i32, i32)* @_ZN9ClassTestC2Eii
        """
        reference = source.split()[-1]
        return DeclarationContainer(instruction=instruction, reference_declaration=ReferenceDeclaration(name=LlvmReferenceName(name), reference=LlvmReferenceName(reference)))

    def parse(self, instruction: LlvmSourceLine) -> DeclarationContainer:
        """
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i3}2 3], align 4
        @_ZN9ClassTestC1Eii = dso_local unnamed_addr alias void (%class.ClassTest*, i32, i32), void (%class.ClassTest*, i32, i32)* @_ZN9ClassTestC2Eii
        %class.ClassTest = type { i32, i32 }
        """
        assignment = instruction.line.split("=")
        name = assignment[0].strip()    
        source = assignment[1]
        if name.startswith("@__const."):
            return self._parse_const(name=name, source=source, instruction=instruction)
        if name.startswith("%class."):
            return self._parse_class(name=name, source=source, instruction=instruction)
        if name.startswith("@"):
            return self._parse_reference(name=name, source=source, instruction=instruction)
        assert False, f"Could not parse instruction {instruction}"


class LlvmParser:

    _comment_line_start = ";"

    def __init__(self):
        self._msg = Messages()

    def _parse_constants(self, constants: LlvmSourceConstants) -> ConstantContainer:
        parsed_constants = [LlvmConstantParser().parse(i) for i in constants.lines]
        return ConstantContainer(declarations=parsed_constants)

    def _parse_function(self, source_function: LlvmSourceFunction, llvm_constants: ConstantContainer) -> LlvmFunction:
        return LlvmFunctionParser().parse(source_function=source_function, constants=llvm_constants)

    def _parse_functions(self, source_file: LlvmSourceFile, llvm_constants: ConstantContainer) -> LlvmFunctionContainer:
        functions: LlvmSourceFunctions = LlvmSourceFileParser().extract_functions(source_file=source_file)
        parsed_funtions = [self._parse_function(source_function=i, llvm_constants=llvm_constants) for i in functions.functions]
        return LlvmFunctionContainer(functions=parsed_funtions)

    def parse(self, text: List[str]) -> LlvmModule:
        source_file = LlvmSourceFileParser().load(lines=text)
        constants = LlvmSourceFileParser().extract_constants(source_file=source_file)
        llvm_constants = self._parse_constants(constants=constants)
        llvm_functions = self._parse_functions(source_file=source_file, llvm_constants=llvm_constants)
        return LlvmModule(functions=llvm_functions, constants=llvm_constants)
