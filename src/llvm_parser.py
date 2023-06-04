
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Union
from instruction import AllocaInstruction, BitcastInstruction, CallInstruction, GetelementptrInstruction, DefaultInstruction, LoadInstruction, ReturnInstruction
from instruction_argument import InstructionArgument, InstructionArgumentContainer
from instruction_interface import InstructionInterface, LlvmOutputPort, MemoryInterface
from llvm_destination import LlvmDestination
from llvm_globals_container import GlobalsContainer
from llvm_function import LlvmFunction, LlvmFunctionContainer
from llvm_global_parser import LlvmGlobalParser
from llvm_instruction import LlvmInstructionContainer, LlvmInstructionInstance, LlvmInstructionInterface
from llvm_intruction_parser import LlvmInstructionParserInterface, LlvmInstructionParserArguments
from llvm_module import LlvmModule
from llvm_source_file import LlvmSourceConstants, LlvmSourceFile, LlvmSourceFileParser, LlvmSourceFunction, LlvmSourceFunctions, LlvmSourceLine

from messages import Messages
from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmVariableName, LlvmTypeFactory
from llvm_declarations import LlvmDeclarationFactory, LlvmPointerDeclaration, LlvmIntegerDeclaration

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

    def _new_depth(self, letter: str, depth: int, string: str) -> int:
        if letter == "(":
            depth += 1
        elif letter == ")":
            depth += -1
        assert depth >= 0, f"Found more left paranthesis than right paranthesis in {string}"
        return depth

    def _split_top(self, string: str, splitter: str) -> List[str]:
        ''' Splits strings at occurance of 'splitter' but only if not enclosed by brackets.
            Removes all whitespace immediately after each splitter.
            This assumes brackets, braces, and parens are properly matched - may fail otherwise '''
        outlist = []
        outstring: List[str] = []
        depth = 0
        for letter in string:
            depth = self._new_depth(letter=letter, depth=depth, string=string)
            if not depth and letter == splitter:
                outlist.append("".join(outstring))
                outstring = []
            else:
                outstring.append(letter)
        outlist.append("".join(outstring))
        return outlist
    
    def _split(self, x: str, split_char: str) -> List[str]:
        return self._remove_empty_elements(x.split(split_char))

    def split_equal_sign(self, x: str) -> List[str]:
        return self._split(x, '=')

    def split_space(self, x: str) -> List[str]:
        return self._split(x, ' ')

    def split_top_space(self, x: str) -> List[str]:
        return self._remove_empty_elements(self._split_top(string=x, splitter=" "))

    def split_comma(self, x: str) -> List[str]:
        return self._split(x, ',')

    def split_top_comma(self, x: str) -> List[str]:
        return self._remove_empty_elements(self._split_top(string=x, splitter=","))

    def get_list_element(self, x : Union[List[str], Tuple[str, str, str]], index : int) -> str:
        return x[index].strip()

    def remove_first_word(self, text : str) -> str:
        return text.strip().partition(' ')[2]

    def first_word(self, text: str) -> str:
        return text.split()[0]

@dataclass
class LlvmInstructionLabel(LlvmInstructionInterface):
    name: str
    def is_valid(self) -> bool:
        return False
    
@dataclass
class LlvmInstructionCommand(LlvmInstructionInterface):
    destination: LlvmDestination
    instruction: InstructionInterface
    def is_valid(self) -> bool:
        return self.instruction.is_valid()
    def get_destination(self) -> Optional[LlvmVariableName]:
        return self.destination.name
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return self.instruction.get_output_port()
    def get_operands(self) -> Optional[InstructionArgumentContainer]:
        return self.instruction.get_operands()
    def get_data_type(self) -> Optional[TypeDeclaration]:
        return self.instruction.get_data_type()
    def get_library(self) -> str:
        return self.instruction.get_library()
    def get_instance_name(self) -> str:
        return self.instruction.get_instance_name()
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return self.instruction.get_memory_interface()
    def access_memory_contents(self) -> bool:
        return self.instruction.access_memory_contents()
    def map_function_arguments(self) -> bool:
        return self.instruction.map_function_arguments()
    def is_return_instruction(self) -> bool:
        return self.instruction.is_return_instruction()
    def get_memory_drivers(self, pointer_name: str) -> List[str]:
        operands = self.get_operands()
        if operands is None:
            return []
        operand_pointer_names = operands.get_pointer_names()
        if pointer_name in operand_pointer_names:
            return [self.get_instance_name()]
        return []
    def get_pointer_destinations(self) -> List[LlvmDestination]:
        return [self.destination] if self.instruction.returns_pointer() else []        

class LlvmInstructionLabelParser:

    def parse(self, source_line: LlvmSourceLine) -> LlvmInstructionLabel:
        """
        entry:
        """
        name = source_line.line.split(":")[0]
        return LlvmInstructionLabel(name=name, source_line=source_line)

class BitCastInstructionParser(LlvmInstructionParserInterface):

    def parse(self, arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> InstructionInterface:
        utils = LlvmParserUtilities()
        c = utils.split_space(arguments.instruction)
        opcode = c[0]
        data_width = int(" ".join(c[1:-3]))
        data_type = LlvmIntegerDeclaration(data_width=data_width)
        signal_name = LlvmVariableName(c[-3])
        argument = InstructionArgument(signal_name=signal_name, data_type=data_type)
        operands = [argument]
        return BitcastInstruction(
            opcode=opcode, data_type=data_type, operands=InstructionArgumentContainer(operands)
        )

    def match(self, instruction: List[str]) -> bool:
        return instruction[0] == "bitcast"

class GetelementptrInstructionParser(LlvmInstructionParserInterface):
    
    def parse(self, arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> InstructionInterface:
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
        return GetelementptrInstruction(destination=destination, opcode=opcode, data_type=signal_data_type, operands=InstructionArgumentContainer(operands), offset=pointer_offset)

    def match(self, instruction: List[str]) -> bool:
        return instruction[0] == "getelementptr"

class ReturnInstructionParser(LlvmInstructionParserInterface):

    def parse(self, arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> InstructionInterface:
        """
        instruction is expected to be one of:
            "ret i32 %add"
            "ref float %add"
            "ret void"
        """
        utils = LlvmParserUtilities()
        a = utils.split_space(arguments.instruction)
        opcode = a[0].strip()
        data_type_position = a[1].strip()
        data_type = LlvmDeclarationFactory().get(data_type=data_type_position, constants=arguments.constants)
        try:
            signal_name = LlvmVariableName(a[2].strip())
            argument = InstructionArgument(signal_name=signal_name, data_type=data_type)
            operands = [argument]
        except IndexError:
            operands = []
        return ReturnInstruction(opcode=opcode, data_type=data_type, operands=InstructionArgumentContainer(operands))

    def match(self, instruction: List[str]) -> bool:
        return instruction[0] == "ret"

class AllocaInstructionParser(LlvmInstructionParserInterface):

    def parse(self, arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> InstructionInterface:
        # alloca [3 x i32], align 4
        # alloca i32, align 4
        # alloca %class.ClassTest, align 4
        assert False, f"alloca is not supported yet: {source_line.get_elaborated()}. It is propably caused by defining a non static variable"
        x = arguments.instruction.split(",")
        y = x[0].split(maxsplit=1)
        opcode = y[0]
        data_type_position = y[1].replace("[", "").replace("]", "")
        data_type = LlvmDeclarationFactory().get(data_type=data_type_position, constants=arguments.constants)
        initialization = arguments.constants.get_initialization(name=arguments.destination.name)
        return AllocaInstruction(
            opcode=opcode, data_type=data_type, output_port_name=arguments.destination.name, initialization=initialization
        )

    def match(self, instruction: List[str]) -> bool:
        return instruction[0] == "alloca"

class CallInstructionParser(LlvmInstructionParserInterface):

    def _split_function_call_from_arguments(self, text: str) -> Tuple[str, str]:
        split_text = text.split('(', maxsplit=1)
        function_call = split_text[0]
        arguments = split_text[1].rsplit(')', maxsplit=1)[0]
        return function_call, arguments

    def _is_ignored_function_call(self, name: str) -> bool:
        ignored_functions = ["@llvm.lifetime"]
        return any(name.startswith(i) for i in ignored_functions)

    def _get_call_instruction(self, function_name: str, llvm_function: bool, return_type: str, arguments: str, source_line: LlvmSourceLine) -> CallInstruction:
        data_type = LlvmDeclarationFactory().get(return_type)
        operands = LlvmArgumentParser().parse(arguments=arguments, unnamed=True)
        return CallInstruction(opcode=function_name, llvm_function=llvm_function, data_type=data_type, operands=InstructionArgumentContainer(operands), source_line=source_line)

    def _split_function_call(self, function_call: str) -> Tuple[str, str]:
        head_split = function_call.split()
        function_name = head_split[-1]
        return_type = head_split[-2]
        return function_name, return_type

    def parse(self,  arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> Optional[InstructionInterface]:
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
        return self._get_call_instruction(function_name=function_name, llvm_function=llvm_function, 
                                          return_type=return_type, arguments=function_arguments,
                                          source_line=source_line)

    def match(self, instruction: List[str]) -> bool:
        return instruction[0] == "call" or instruction[:2] == ["tail", "call"]

class LoadInstructionParser(LlvmInstructionParserInterface):

    def parse(self, arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> InstructionInterface:
        '''
        "load i32, i32* %a.addr, align 4"
        "load float, ptr getelementptr inbounds ([4 x float], ptr @_ZZ3firfE6buffer, i64 0, i64 2), align 8, !tbaa !5"
        '''
        utils = LlvmParserUtilities()
        x = utils.split_top_comma(arguments.instruction)
        y = x[0].split(maxsplit=1)
        opcode = y[0]
        data_type = LlvmDeclarationFactory().get(data_type=y[1], constants=arguments.constants)
        operands = LlvmArgumentParser().parse(arguments=x[1], unnamed=True)
        return LoadInstruction(
            opcode=opcode, data_type=data_type, output_port_name=arguments.destination.name, operands=InstructionArgumentContainer(operands), source_line=source_line
        )

    def match(self, instruction: List[str]) -> bool:
        return instruction[0] == "load"

class DefaultInstructionParser(LlvmInstructionParserInterface):

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
        """
        1) add nsw i32 %0, %1
        2) sub nsw i32 %0, %1
        """
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
            "fcmp ule float %0, %mul.i"
        """
        return {
            "icmp": InstructionPosition(opcode=1, data_type=2, operands=[(2, 3), (2, 4)]),
            "zext": InstructionPosition(opcode=0, data_type=1, operands=[(1, 2)]),
            "trunc": InstructionPosition(opcode=0, data_type=4, operands=[(1, 2)]),
            "select": InstructionPosition(opcode=0, data_type=3, operands=[(1, 2), (3, 4), (5, 6)]),
            "store": InstructionPosition(opcode=0, data_type=1, operands=[(1, 2), (3, 4)]),
            "fcmp": InstructionPosition(opcode=0, sub_type=1, data_type=2, operands=[(2, 3), (2, 4)])}

    def _get_instruction_positions(self) -> Dict[str, InstructionPosition]:
        dict_1 = self._get_type_and_two_arguments_instructions()
        dict_2 = self._get_arithmetic_instructions()
        dict_3 = self._get_special_instructions()
        return dict_1 | dict_2 | dict_3

    def parse(self,  arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> InstructionInterface:
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
            operands=InstructionArgumentContainer(x.operands),
            output_port_name="m_tdata",
            source_line=source_line
        )

    def match(self, instruction: List[str]) -> bool:
        return True

class LlvmInstructionCommandParser:

    def __init__(self):
        self._msg = Messages()

    def _parse_instruction(self, arguments: LlvmInstructionParserArguments, destination: LlvmDestination, source_line: LlvmSourceLine) -> Optional[InstructionInterface]:
        parsers: List[LlvmInstructionParserInterface] =  [
            BitCastInstructionParser(),
            GetelementptrInstructionParser(),
            ReturnInstructionParser(),
            AllocaInstructionParser(),
            CallInstructionParser(),
            LoadInstructionParser()]
        instruction_words = arguments.instruction.split()
        parser: LlvmInstructionParserInterface = DefaultInstructionParser()
        for i in parsers:
            if i.match(instruction_words):
                parser = i
        return parser.parse(arguments=arguments, destination=destination, source_line=source_line)

    def parse(self, source_line: LlvmSourceLine, constants: GlobalsContainer) -> Optional[LlvmInstructionCommand]:
        """
        1)    %add = add nsw i32 %b, %a
        2)    ret i32 %add
        """
        destination_name = None
        source = source_line.line
        utils = LlvmParserUtilities()
        if source_line.is_assignment():
            x = source_line.line.split("=")
            destination_name = LlvmVariableName(utils.get_list_element(x, 0))
            source = utils.get_list_element(x, 1)
        destination = LlvmDestination(name=destination_name)
        arguments = LlvmInstructionParserArguments(instruction=source, destination=destination, constants=constants)
        instruction = self._parse_instruction(arguments=arguments, destination=destination, source_line=source_line)
        return LlvmInstructionCommand(destination=destination, instruction=instruction, source_line=source_line) if instruction is not None else None

class LlvmArgumentParser:

    def __init__(self) -> None:
        self._msg = Messages()

    def _parse_argument(self, argument_item: str, unnamed: bool) -> InstructionArgument:
        utils = LlvmParserUtilities()
        """
        1) i = "i32 2"
        2) i = "i32* nonnull %n"
        3) i = "ptr noundef nonnull align 4 dereferenceable(12) getelementptr inbounds ([4 x float], ptr @_ZZ3firfE6buffer, i64 0, i64 1)"
        4) i = "ptr noundef nonnull align 16 dereferenceable(12) @_ZZ3firfE6buffer"
        """
        elements = utils.split_top_space(argument_item) 
        # 1) g = ["i32", "2"]
        # 2) g = ["i32*", "nonnull",  "%n"]
        # 3) g = ["ptr", "noundef", "nonnull", "align", "4", "dereferenceable(12)", "getelementptr", "inbounds", "([4 x float], ptr @_ZZ3firfE6buffer, i64 0, i64 1)"]
        argument_type = utils.get_list_element(elements, 0)
        data_type = LlvmDeclarationFactory().get(data_type=argument_type)
        argument_value = utils.get_list_element(elements, -1)
        argument = data_type.resolve_type(argument_value)
        # 1) signal_name = "2"
        # 2) signal_name = "%n"
        return InstructionArgument(signal_name=argument, data_type=data_type, unnamed=unnamed)

    def parse(self, arguments: str, unnamed: bool = False) -> List[InstructionArgument]:
        """
        arguments = "i32 2, i32* nonnull %n"
        arguments = ptr nocapture noundef readonly %a
        arguments = ptr noundef nonnull align 4 dereferenceable(8 %a, i32 noundef 1, i32 noundef 2
        """
        utils = LlvmParserUtilities()
        return [
            self._parse_argument(argument_item=i, unnamed=unnamed)
            for i in utils.split_top_comma(arguments)
        ]

class LlvmGeneralInstructionParser:

    def _parse_line(self, line: LlvmSourceLine, constants: GlobalsContainer) -> Optional[LlvmInstructionInterface]:
        if line.is_label():
            return LlvmInstructionLabelParser().parse(source_line=line)
        if line.is_end_bracket():
            return None
        return LlvmInstructionCommandParser().parse(source_line=line, constants=constants)

    def parse(self, lines: List[LlvmSourceLine], constants: GlobalsContainer) -> List[LlvmInstructionInstance]:
        """
        entry:
            %add = add nsw i32 %b, %a
            ret i32 %add
        """
        x = [self._parse_line(line=i, constants=constants) for i in lines]
        return [LlvmInstructionInstance(instruction=i, instance_index=index) for index, i in enumerate(x) if i is not None]

class LlvmFunctionParser:
    
    def __init__(self) -> None:
        self._msg = Messages()

    def _parse_parenthesis(self, left_parenthis_split: List[str]) -> Tuple[str, TypeDeclaration]:
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
        function_name, return_type = self._parse_parenthesis(left_parenthis_split=left_parenthis_split)
        return function_name, arguments, return_type

    def parse(self, source_function: LlvmSourceFunction, constants: GlobalsContainer) -> LlvmFunction:
        """
        define dso_local noundef i32 @_Z3addii(i32 noundef %a, i32 noundef %b) local_unnamed_addr #0 {
        entry:
            %add = add nsw i32 %b, %a
            ret i32 %add
        }
        """
        function_name, arguments, return_type = self._parse_function_description(source_function.lines[0].line)
        comands_excluding_description = source_function.lines[1:]
        instructions = LlvmGeneralInstructionParser().parse(lines=comands_excluding_description, constants=constants)
        return LlvmFunction(name=function_name, arguments=InstructionArgumentContainer(arguments), return_type=return_type, instructions=LlvmInstructionContainer(instructions))

class LlvmParser:

    _comment_line_start = ";"

    def __init__(self):
        self._msg = Messages()

    def _parse_globals(self, constants: LlvmSourceConstants) -> GlobalsContainer:
        parsed_constants = [LlvmGlobalParser().parse(i) for i in constants.lines]
        return GlobalsContainer(declarations=parsed_constants)

    def _parse_function(self, source_function: LlvmSourceFunction, llvm_constants: GlobalsContainer) -> LlvmFunction:
        return LlvmFunctionParser().parse(source_function=source_function, constants=llvm_constants)

    def _parse_functions(self, source_file: LlvmSourceFile, llvm_constants: GlobalsContainer) -> LlvmFunctionContainer:
        functions: LlvmSourceFunctions = LlvmSourceFileParser().extract_functions(source_file=source_file)
        parsed_funtions = [self._parse_function(source_function=i, llvm_constants=llvm_constants) for i in functions.functions]
        return LlvmFunctionContainer(functions=parsed_funtions)

    def parse(self, text: List[str]) -> LlvmModule:
        source_file = LlvmSourceFileParser().load(lines=text)
        constants = LlvmSourceFileParser().extract_constants(source_file=source_file)
        llvm_constants = self._parse_globals(constants=constants)
        llvm_functions = self._parse_functions(source_file=source_file, llvm_constants=llvm_constants)
        return LlvmModule(functions=llvm_functions, globals=llvm_constants)
