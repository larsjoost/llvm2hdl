from abc import ABC, abstractmethod
from cgitb import reset
from dataclasses import dataclass, field
import re
from typing import Dict, List, Tuple, Optional, Union

from messages import Messages
from llvm_declarations import LlvmArrayDeclaration, LlvmPointerDeclaration, TypeDeclaration, LlvmDeclaration, LlvmName, LlvmType, LlvmTypeFactory
from vhdl_declarations import VhdlDeclarations

@dataclass
class Constant:
    value: str
    data_type: LlvmDeclaration

@dataclass
class ConstantDeclaration:
    name: str
    type: LlvmDeclaration
    values: List[Constant]
    def get_name(self) -> str:
        return self.name.rsplit(".", maxsplit=1)[-1]
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.type.get_dimensions()
    def get_values(self) -> List[str]:
        return [i.value for i in self.values]

@dataclass
class InstructionArgument:
    signal_name: LlvmType
    data_type : TypeDeclaration
    port_name: Optional[str] = None
    def get_dimensions(self) -> Tuple[int, Optional[str]]:
        return self.data_type.get_dimensions()
    def single_dimension(self) -> bool:
        return self.data_type.single_dimension()
    def is_pointer(self) -> bool:
        return self.data_type.is_pointer()
    def get_array_index(self) -> Optional[str]:
        return self.data_type.get_array_index()
    def get_name(self) -> str:
        return self.signal_name.get_name()
    def get_value(self) -> str:
        return self.signal_name.get_value()
    def get_data_width(self) -> str:
        return self.data_type.get_data_width()
    def is_integer(self) -> bool:
        if isinstance(self.signal_name, LlvmType):
            return self.signal_name.is_integer()
        return False

@dataclass
class LlvmOutputPort:
    data_type : TypeDeclaration
    port_name: Optional[Union[LlvmName, str]] = None
    def get_type_declarations(self) -> str:
        return VhdlDeclarations(self.data_type).get_type_declarations()
    def is_pointer(self) -> bool:
        return False
    def get_name(self) -> Optional[str]:
        if isinstance(self.port_name, LlvmName):
            return self.port_name.get_name()
        return self.port_name
    def is_void(self) -> bool:
        return self.data_type.is_void()

@dataclass
class LlvmMemoryOutputPort(LlvmOutputPort):
    def is_pointer(self) -> bool:
        return True

class MemoryInterface(ABC):
    def is_master(self) -> bool:
        return False

class MemoryInterfaceMaster(MemoryInterface):
    def is_master(self) -> bool:
        return True

class MemoryInterfaceSlave(MemoryInterface):
    pass

@dataclass
class InstructionPosition:
    opcode: int
    operands: List[Tuple[int, int]]
    data_type: int
    memory_interface: Optional[MemoryInterface] = None

class InstructionPositionParser:
    source : List[str]
    opcode : str
    operands : List[InstructionArgument]
    data_type : str
    memory_interface: Optional[MemoryInterface]
    def __init__(self, instruction: List[str], position: InstructionPosition):
        self.source = instruction
        self.memory_interface = position.memory_interface
        self.opcode = instruction[position.opcode]
        self.data_type = instruction[position.data_type].replace(",", "")
        self.operands = [self._parse_operand(instruction, item, index) for index, item in enumerate(position.operands)]
    def _parse_operand(self, instruction: List[str], item: Tuple[int, int], index: int) -> InstructionArgument:
        type_index, value_index = item
        value = instruction[value_index]
        signal_name = LlvmTypeFactory(value.replace(",","")).resolve()
        port_name = chr(ord('a') + index)
        data_type = LlvmDeclaration(instruction[type_index].replace(",", ""))
        return InstructionArgument(port_name=port_name, signal_name=signal_name, data_type=data_type)
    def __str__(self) -> str:
        return str(vars(self))

class LlvmParserException(Exception):
    pass


@dataclass
class Instruction(ABC):
    opcode: str
    data_type: TypeDeclaration
    operands: List[InstructionArgument] = field(default_factory=list)
    output_port_name: Optional[Union[LlvmName, str]] = None
    memory_interface: Optional[MemoryInterface] = None
    def get_output_port(self) -> LlvmOutputPort:
        return LlvmOutputPort(data_type=self.data_type, port_name=self.output_port_name)
    def get_instance_name(self) -> str:
        return f"llvm_{self.opcode}"
    def get_library(self) -> str:
        return "llvm"
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return self.memory_interface
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False

@dataclass
class ReturnInstruction(Instruction):
    pass

@dataclass
class BitcastInstruction(Instruction):
    def is_valid(self) -> bool:
        return False

@dataclass
class AllocaInstruction(Instruction):
    def get_generic_map(self) -> Optional[List[str]]:
        data_width = self.data_type.get_data_width()
        return [f"size => {data_width}/8"]
    def get_memory_interface(self) -> MemoryInterface:
        return MemoryInterfaceSlave()
    def get_output_port(self) -> LlvmOutputPort:
        return LlvmMemoryOutputPort(data_type=self.data_type, port_name=self.output_port_name)
    def is_memory(self) -> bool:
        return True

@dataclass
class GetelementptrInstruction(Instruction):
    pass

@dataclass
class CallInstruction(Instruction):
    def get_instance_name(self) -> str:
        return self.opcode
    def get_library(self) -> str:
        return "work"
    def map_function_arguments(self) -> bool:
        return True
    
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
        self._msg.function_start(f"x={str(x)}, index={index}")
        result = x[index].strip()
        self._msg.function_end(result)
        return result

    def remove_first_word(self, text : str) -> str:
        return text.strip().partition(' ')[2]

    def first_word(self, text: str) -> str:
        return text.split()[0]

@dataclass
class LlvmInstruction(ABC):
    def get_destination(self) -> Optional[LlvmName]:
        return None
    def get_output_port(self) -> Optional[LlvmOutputPort]:
        return None
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return None
    def get_data_type(self) -> Optional[TypeDeclaration]:
        return None
    def get_library(self) -> Optional[str]:
        return None
    def get_instance_name(self) -> Optional[str]:
        return None
    def get_generic_map(self) -> Optional[List[str]]:
        return None
    def get_memory_interface(self) -> Optional[MemoryInterface]:
        return None
    def is_valid(self) -> bool:
        return True
    def is_memory(self) -> bool:
        return False
    def map_function_arguments(self) -> bool:
        return False

@dataclass
class LlvmInstructionLabel(LlvmInstruction):
    name: str
    def is_valid(self) -> bool:
        return False

@dataclass
class LlvmInstructionCommand(LlvmInstruction):
    destination: Optional[LlvmName]
    instruction: Instruction
    def is_valid(self) -> bool:
        return self.instruction.is_valid()
    def get_destination(self) -> Optional[LlvmName]:
        return self.destination
    def get_output_port(self) -> LlvmOutputPort:
        return self.instruction.get_output_port()
    def get_operands(self) -> Optional[List[InstructionArgument]]:
        return self.instruction.operands
    def get_data_type(self) -> Optional[TypeDeclaration]:
        return self.instruction.data_type
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

@dataclass
class LlvmFunction:
    name: str
    arguments: List[InstructionArgument]
    return_type : LlvmDeclaration
    instructions: List[LlvmInstruction]
 
class LlvmInstructionLabelParser:

    def parse(self, text: str) -> LlvmInstructionLabel:
        """
        entry:
        """
        name = text.split(":")[0]
        return LlvmInstructionLabel(name=name)

class InstructionParser(ABC):

    def __init__(self):
        self._msg = Messages()

    @abstractmethod
    def parse(self, instruction: str, destination: Optional[LlvmName]) -> Optional[Instruction]:
        pass

class BitCastInstructionParser(InstructionParser):

    def parse(self, instruction: str, destination: Optional[LlvmName]) -> Instruction:
        self._msg.function_start(f"instruction={instruction}")
        utils = LlvmParserUtilities()
        c = utils.split_space(instruction)
        opcode = c[0]
        data_type = LlvmDeclaration(" ".join(c[1:-3]))
        signal_name = LlvmName(c[-3])
        argument = InstructionArgument(signal_name=signal_name, data_type=data_type)
        operands = [argument]
        result = BitcastInstruction(opcode=opcode, data_type=data_type, operands=operands)
        self._msg.function_end(result)
        return result

class GetelementptrInstructionParser(InstructionParser):

    def parse(self, instruction: str, destination: Optional[LlvmName]) -> Instruction:
        self._msg.function_start(f"instruction={instruction}")
        array_index = instruction.rsplit(maxsplit=1)[-1]
        opcode = instruction.split()[0]
        utils = LlvmParserUtilities()
        c = utils.split_comma(instruction)
        d = c[1].rsplit(maxsplit=1)
        data_type = LlvmArrayDeclaration(data_type=d[0], index=array_index)
        signal_name = LlvmName(d[1])
        argument = InstructionArgument(signal_name=signal_name, data_type=data_type)
        operands = [argument]
        result = GetelementptrInstruction(opcode=opcode, data_type=data_type, operands=operands)

        self._msg.function_end(result)
        return result

class ReturnInstructionParser(InstructionParser):

    def parse(self, instruction : str, destination: Optional[LlvmName]) -> Instruction:
        """
        instruction is expected to be one of:
            "ret i32 %add"
            "ret void"
        """
        utils = LlvmParserUtilities()
        a = utils.split_space(instruction)
        opcode = a[0]
        data_type = LlvmDeclaration(a[1].strip())
        try:
            signal_name = LlvmName(a[2].strip())
            argument = InstructionArgument(signal_name=signal_name, data_type=data_type)
            operands = [argument]
        except IndexError:
            operands = []
        return ReturnInstruction(opcode=opcode, data_type=data_type, operands=operands)

class AllocaInstructionParser(InstructionParser):

    def parse(self, instruction: str, destination: Optional[LlvmName]) -> Instruction:
        self._msg.function_start(f"instruction={instruction}")
        x = instruction.split(",")
        y = x[0].split(maxsplit=1)
        opcode = y[0]
        data_type_position = y[1].replace("[", "").replace("]", "")
        data_type = LlvmPointerDeclaration(data_type=data_type_position)
        result = AllocaInstruction(opcode=opcode, data_type=data_type, output_port_name=destination)
        self._msg.function_end(result)
        return result

class CallInstructionParser(InstructionParser):

    def get_entity_name(self, name: str) -> str:
        return "entity" + name.replace("@", "")

    def _split_parenthesis(self, text: str) -> Tuple[str, str]:
        self._msg.function_start(f"text={text}")
        split_text = text.partition('(')
        head = split_text[0]
        tail = split_text[2].partition(')')[0]
        result = head, tail
        self._msg.function_end(result)
        return result

    def _is_ignored_function_call(self, name: str) -> bool:
        self._msg.function_start(f"name={name}")
        ignored_functions = ["@llvm.lifetime"]
        result = any(name.startswith(i) for i in ignored_functions)
        self._msg.function_end(result)
        return result

    def parse(self, instruction: str, destination: Optional[LlvmName]) -> Optional[Instruction]:
        """
        instruction is expected to be one of: 
            "call i32 @_Z3addii(i32 2, i32 3)"
            "tail call i32 @_Z3addii(i32 2, i32 3)"
        """
        self._msg.function_start(f"instruction={instruction}")
        head, tail = self._split_parenthesis(instruction)
        # 1) head = "call i32 @_Z3addii"
        # 2) head = "tail call i32 @_Z3addii"
        # tail = "i32 2, i32 3"
        head_split = head.split()
        function_name = head_split[-1]
        if self._is_ignored_function_call(name=function_name):
            return None
        name = self.get_entity_name(function_name)
        data_type = LlvmDeclaration(head_split[-2])
        arguments = LlvmArgumentParser().parse(arguments=tail)
        result = CallInstruction(opcode=name, operands=arguments, data_type=data_type, output_port_name=None)
        self._msg.function_end(result)
        return result

class DefaultInstructionParser(InstructionParser):

    def _get_type_and_two_arguments_instructions(self) -> Dict[str, InstructionPosition]:
        """
        The instruction is expected to be in one of the following formats:
            "fadd float %0, %1"
            "or i1 %cmp, %cmp2"
            "ashr i32 %a, %b" 
        """
        position = InstructionPosition(opcode=0, data_type=1, operands=[(1, 2), (1, 3)]) 
        commands = ["fadd", "xor", "and", "or", "ashr", "lshr", "shl"]
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
        """
        return {
            "icmp": InstructionPosition(opcode=1, data_type=2, operands=[(2, 3), (2, 4)]),
            "zext": InstructionPosition(opcode=0, data_type=1, operands=[(1, 2)]),
            "trunc": InstructionPosition(opcode=0, data_type=4, operands=[(1, 2)]),
            "select": InstructionPosition(opcode=0, data_type=3, operands=[(1, 2), (3, 4), (5, 6)]),
            "store": InstructionPosition(opcode=0, data_type=1, operands=[(1, 2), (3, 4)], memory_interface=MemoryInterfaceMaster()),
            "load": InstructionPosition(opcode=0, data_type=1, operands=[(2, 3)], memory_interface=MemoryInterfaceMaster())}

    def _get_instruction_positions(self) -> Dict[str, InstructionPosition]:
        dict_1 = self._get_type_and_two_arguments_instructions()
        dict_2 = self._get_arithmetic_instructions()
        dict_3 = self._get_special_instructions()
        return dict_1 | dict_2 | dict_3

    def parse(self, instruction: str, destination: Optional[LlvmName]) -> Instruction:
        self._msg.function_start(f"instruction={instruction}")
        utils = LlvmParserUtilities()
        a = utils.split_space(instruction)
        position: Dict[str, InstructionPosition] = self._get_instruction_positions()
        opcode = utils.get_list_element(a, 0)
        x = InstructionPositionParser(instruction=a, position=position[opcode])
        result = Instruction(opcode=x.opcode, operands=x.operands, data_type=LlvmDeclaration(x.data_type), output_port_name="m_tdata", memory_interface=x.memory_interface)
        self._msg.function_end(result)
        return result

class LlvmInstructionCommandParser:

    def __init__(self):
        self._msg = Messages()

    def _parse_instruction(self, instruction: str, destination: Optional[LlvmName]) -> Optional[Instruction]:
        self._msg.function_start(f"instruction={instruction}")
        parsers: Dict[str, InstructionParser] =  {
            "bitcast": BitCastInstructionParser(),
            "getelementptr": GetelementptrInstructionParser(),
            "ret": ReturnInstructionParser(),
            "alloca": AllocaInstructionParser(),
            "call": CallInstructionParser()}
        instruction_words = instruction.split()
        parser: InstructionParser = DefaultInstructionParser()
        for i in parsers:
            if i in instruction_words:
                parser = parsers[i]
        result = parser.parse(instruction=instruction, destination=destination)
        self._msg.function_end(result)
        return result

    def parse(self, text: str) -> Optional[LlvmInstructionCommand]:
        """
        1)    %add = add nsw i32 %b, %a
        2)    ret i32 %add
        """
        destination = None
        source = text
        utils = LlvmParserUtilities()
        if "=" in text:
            x = text.split("=")
            destination = LlvmName(utils.get_list_element(x, 0))
            source = utils.get_list_element(x, 1)
        instruction = self._parse_instruction(instruction=source, destination=destination)
        return LlvmInstructionCommand(destination=destination, instruction=instruction) if instruction is not None else None

class LlvmArgumentParser:

    def __init__(self) -> None:
        self._msg = Messages()

    def parse(self, arguments: str) -> List[InstructionArgument]:
        self._msg.function_start(f"arguments={arguments}")
        # arguments = "i32 2, i32* nonnull %n"
        result = []
        utils = LlvmParserUtilities()
        for i in utils.split_comma(arguments):
            # 1) i = "i32 2"
            # 2) i = "i32* nonnull %n"
            g = utils.split_space(i) 
            # 1) g = ["i32", "2"]
            # 2) b = ["i32*", "nonnull",  "%n"]
            data_type = LlvmDeclaration(utils.get_list_element(g, 0))
            argument = LlvmTypeFactory(utils.get_list_element(g, -1)).resolve()
            # 1) signal_name = "2"
            # 2) signal_name = "%n"
            result.append(InstructionArgument(signal_name=argument, data_type=data_type))
        self._msg.function_end(result)
        return result

class LlvmInstructionParser:

    def _parse_line(self, line: str) -> Optional[LlvmInstruction]:
        if ":" in line:
            return LlvmInstructionLabelParser().parse(line)
        return LlvmInstructionCommandParser().parse(line)

    def parse(self, lines: List[str]) -> List[LlvmInstruction]:
        """
        entry:
            %add = add nsw i32 %b, %a
            ret i32 %add
        """
        x = [self._parse_line(i) for i in lines]
        return [i for i in x if i is not None]

class LlvmFunctionParser:
    
    def __init__(self) -> None:
        self._msg = Messages()

    def _parse_function_description(self, line: str) -> Tuple[str, List[InstructionArgument], LlvmDeclaration]:
        """
        1) line = "define dso_local noundef i32 @_Z3addii(i32 noundef %a, i32 noundef %b) local_unnamed_addr #0 {"
        2) line = "define dso_local void @_ZN9ClassTestC2Eii(%class.ClassTest* nocapture noundef nonnull writeonly align 4 dereferenceable(8) %this, i32 noundef %a, i32 noundef %b) unnamed_addr #0 align 2 {"
        """
        self._msg.function_start(f"line={line}")
        left_parenthis_split = line.split("(", maxsplit=1)
        argument_text = left_parenthis_split[1].rsplit(")", maxsplit=1)[0]
        arguments = LlvmArgumentParser().parse(arguments=argument_text)
        function_definition = left_parenthis_split[0].split()
        function_name = function_definition[-1]
        return_type = LlvmDeclaration(function_definition[-2])
        result = function_name, arguments, return_type
        self._msg.function_end(result)
        return result

    def parse(self, text: str) -> LlvmFunction:
        """
        define dso_local noundef i32 @_Z3addii(i32 noundef %a, i32 noundef %b) local_unnamed_addr #0 {
        entry:
            %add = add nsw i32 %b, %a
            ret i32 %add
        }
        """
        lines = text.split("\n")
        function_name, arguments, return_type = self._parse_function_description(lines[0])
        comands_excluding_right_bracket = lines[1:-2]
        instructions = LlvmInstructionParser().parse(comands_excluding_right_bracket)
        return LlvmFunction(name=function_name, arguments=arguments, return_type=return_type, instructions=instructions)

class LlvmConstantParser:
    
    def __init__(self):
        self._msg = Messages()

    def parse(self, instruction: str) -> Optional[ConstantDeclaration]:
        self._msg.function_start(f"instruction={instruction}", True)
        """
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
        @_ZN9ClassTestC1Eii = dso_local unnamed_addr alias void (%class.ClassTest*, i32, i32), void (%class.ClassTest*, i32, i32)* @_ZN9ClassTestC2Eii
        """
        if " constant " not in instruction:
            return None
        assignment = instruction.split("=")
        name = assignment[0]
        source = assignment[1]
        source_split = source.split("[")
        # source_split = ["private unnamed_addr constant ","3 x i32]", "i32 1, i32 2, i32 3], align 4"]
        definition = source_split[-1].split("]")[0]
        type = LlvmDeclaration(data_type=source_split[1].split("]")[0])
        # definition = "i32 1, i32 2, i32 3"
        definitions: List[Constant] = []
        for i in definition.split(","):
            x = i.split()
            data_type = LlvmDeclaration(data_type=x[0])
            value = x[1]
            definitions.append(Constant(value=value, data_type=data_type))
        result = ConstantDeclaration(name=name, type=type, values=definitions)
        self._msg.function_end(result, True)
        return result

@dataclass
class LlvmModule:
    functions: List[LlvmFunction]
    constants: List[ConstantDeclaration]
    def write_constants(self, file_writer):
        for i in self.constants:
            file_writer.write_constant(constant=i)


class LlvmParser:

    def __init__(self):
        self._msg = Messages()

    def _remove_comments(self, text: str) -> str:
        line_starting_with_semicolon = r';.*'
        return re.sub(line_starting_with_semicolon, '', text)

    def _findall(self, text: str, regex: str) -> List[str]:
        matches = re.finditer(regex, text, re.MULTILINE)
        return [match.group() for match in matches]

    def _extract_functions(self, text: str) -> List[str]:
        self._msg.function_start(f"text={text}")
        match_word_define = r"define "
        all_characters_including_newline = r"(.|\n)*"
        until_right_bracket = r"?\}"
        regex = match_word_define + all_characters_including_newline + until_right_bracket
        result = self._findall(text=text, regex=regex)
        self._msg.function_end(result)
        return result

    def _extract_constants(self, text: str) -> List[str]:
        """
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
        """
        self._msg.function_start(f"text={text}")
        lines = text.split("\n")
        result = [i for i in lines if i.startswith("@")]
        self._msg.function_end(result)
        return result

    def parse(self, text: str) -> LlvmModule:
        self._msg.function_start(f"text={text}")
        without_comments = self._remove_comments(text)
        functions = self._extract_functions(without_comments)
        constants = self._extract_constants(without_comments)
        llvm_functions =[LlvmFunctionParser().parse(i) for i in functions]
        llvm_constants = [i for i in [LlvmConstantParser().parse(i) for i in constants] if i is not None]
        llvm_module = LlvmModule(functions=llvm_functions, constants=llvm_constants)
        self._msg.function_end(llvm_module)
        return llvm_module