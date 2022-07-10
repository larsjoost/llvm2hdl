from abc import ABC
from dataclasses import dataclass
import re
from typing import Dict, List, Tuple, Optional, Union
from assignment_resolution import AssignmentItem

from messages import Messages
from llvm_declarations import LlvmArrayDeclaration, LlvmDeclaration, LlvmName, LlvmType, LlvmTypeFactory
from file_writer import FileWriter
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
class InstructionPosition:
    opcode: int
    operands: List[Tuple[int, int]]
    data_type: int

@dataclass
class InstructionArgument:
    signal_name: LlvmType
    data_type : LlvmDeclaration
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
        if isinstance(self.signal_name, str):
            return self.signal_name
        return self.signal_name.get_name()
    def get_value(self) -> str:
        if isinstance(self.signal_name, str):
            return self.signal_name
        return self.signal_name.get_value()
    def get_data_width(self) -> str:
        return self.data_type.get_data_width()
    def is_integer(self) -> bool:
        if isinstance(self.signal_name, LlvmType):
            return self.signal_name.is_integer()
        return False

@dataclass
class OutputPort:
    data_type : LlvmDeclaration
    port_name: Optional[str] = None
    def get_type_declarations(self) -> str:
        return VhdlDeclarations(self.data_type).get_type_declarations()
    def get_port_map(self) -> str:
        port_map = "m_tdata_i"
        if self.port_name is not None:
            port_map = self.port_name + " => " + port_map
        return port_map

class InstructionParser:
    source : List[str]
    opcode : str
    operands : List[InstructionArgument]
    data_type : str
    def __init__(self, instruction: List[str], position: InstructionPosition):
        self.source = instruction
        self.opcode = instruction[position.opcode]
        self.data_type = instruction[position.data_type]
        self.operands = [self._parse_operand(instruction, item, index) for index, item in enumerate(position.operands)]
    def _parse_operand(self, instruction: List[str], item: Tuple[int, int], index: int) -> InstructionArgument:
        type_index, value_index = item
        value = instruction[value_index]
        signal_name = LlvmTypeFactory(value.replace(",", "")).resolve()
        port_name = chr(ord('a') + index)
        data_type = LlvmDeclaration(instruction[type_index])
        return InstructionArgument(port_name=port_name, signal_name=signal_name, data_type=data_type)
    def __str__(self) -> str:
        return str(vars(self))

@dataclass
class Instruction:
    library: str
    opcode: str
    operands: List[InstructionArgument]
    data_type: LlvmDeclaration
    output_port_name: Optional[str]
    def get_output_port(self) -> OutputPort:
        return OutputPort(data_type=self.data_type, port_name=self.output_port_name)

class LlvmParserException(Exception):
    pass

@dataclass
class EqualAssignment:
    destination : Optional[LlvmName]
    source : str

    
@dataclass
class ReturnInstruction:
    value : Optional[LlvmName]
    data_type : LlvmDeclaration
    
@dataclass
class Alloca:
    data_type : LlvmDeclaration


class LlvmParserUtilities:

    def __init__(self):
        self._msg = Messages()

    def _remove_empty_elements(self, x: List[str]) -> List[str]:
        return [i for i in x if len(i) > 0]

    def _split(self, x: str, split_char: str) -> List[str]:
        return self._remove_empty_elements(x.split(split_char))

    def _split_equal_sign(self, x: str) -> List[str]:
        return self._split(x, '=')

    def _split_space(self, x: str) -> List[str]:
        return self._split(x, ' ')

    def _split_comma(self, x: str) -> List[str]:
        return self._split(x, ',')

    def _get_list_element(self, x : Union[List[str], Tuple[str, str, str]], index : int) -> str:
        self._msg.function_start("_get_list_element(x=" + str(x) + ", index=" + str(index))
        result = x[index].strip()
        self._msg.function_end("_get_list_element = " + str(result))
        return result

    def _remove_first_word(self, text : str) -> str:
        return text.strip().partition(' ')[2]

    def _first_word(self, text: str) -> str:
        return text.split()[0]

@dataclass
class LlvmInstruction(ABC):
    pass

@dataclass
class LlvmInstructionLabel(LlvmInstruction):
    name: str

@dataclass
class LlvmInstructionCommand(LlvmInstruction):
    destination: Optional[LlvmName]
    opcode: str
    source: str

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

class LlvmInstructionCommandParser:

    def parse(self, text: str) -> LlvmInstructionCommand:
        """
        1)    %add = add nsw i32 %b, %a
        2)    ret i32 %add
        """
        destination = None
        source = text
        utils = LlvmParserUtilities()
        if "=" in text:
            x = text.split("=")
            destination = LlvmName(utils._get_list_element(x, 0))
            source = utils._get_list_element(x, 1)
        command = source.strip().split()[0]
        return LlvmInstructionCommand(destination=destination, opcode=command, source=source)

class LlvmArgumentParser:

    def __init__(self) -> None:
        self._msg = Messages()

    def parse(self, arguments: str) -> List[InstructionArgument]:
        self._msg.function_start("arguments=" + arguments)
        # arguments = "i32 2, i32* nonnull %n"
        result = []
        utils = LlvmParserUtilities()
        for i in utils._split_comma(arguments):
            # 1) i = "i32 2"
            # 2) i = "i32* nonnull %n"
            g = utils._split_space(i) 
            # 1) g = ["i32", "2"]
            # 2) b = ["i32*", "nonnull",  "%n"]
            data_type = LlvmDeclaration(utils._get_list_element(g, 0))
            argument = LlvmTypeFactory(utils._get_list_element(g, -1)).resolve()
            # 1) signal_name = "2"
            # 2) signal_name = "%n"
            result.append(InstructionArgument(signal_name=argument, data_type=data_type))
        self._msg.function_end(result)
        return result

class LlvmInstructionParser:

    def _parse_line(self, line: str) -> LlvmInstruction:
        if ":" in line:
            return LlvmInstructionLabelParser().parse(line)
        return LlvmInstructionCommandParser().parse(line)

    def parse(self, lines: List[str]) -> List[LlvmInstruction]:
        """
        entry:
            %add = add nsw i32 %b, %a
            ret i32 %add
        """
        result = [self._parse_line(i) for i in lines]
        return result

class LlvmFunctionParser:
    
    def _parse_function_description(self, line: str) -> Tuple[str, List[InstructionArgument], LlvmDeclaration]:
        """
        line = "define dso_local noundef i32 @_Z3addii(i32 noundef %a, i32 noundef %b) local_unnamed_addr #0 {"
        """
        left_parenthis_split = line.split("(")
        argument_text = left_parenthis_split[1].split(")")[0]
        arguments = LlvmArgumentParser().parse(arguments=argument_text)
        function_definition = left_parenthis_split[0].split()
        function_name = function_definition[-1]
        return_type = LlvmDeclaration(function_definition[-2])
        return function_name, arguments, return_type

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

    def parse(self, instruction: str) -> ConstantDeclaration:
        self._msg.function_start("instruction=" + instruction)
        """
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
        """
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
        self._msg.function_end(result)
        return result

@dataclass
class LlvmModule:
    functions: List[LlvmFunction]
    constants: List[ConstantDeclaration]
    def write_constants(self, file_writer: FileWriter):
        for i in self.constants:
            file_writer.write_constant(constant=i)

class LlvmParser:

    def __init__(self):
        self._msg = Messages()
    
    def get_equal_assignment(self, instruction : str) -> EqualAssignment:
        # 1) instruction = "%0 = load i32, i32* %a.addr, align 4"
        # 2) instruction = "ret i32 %add"
        source: str = instruction
        destination: Optional[LlvmName] = None
        a: Tuple[str, str, str] = source.partition('=')
        # 1) a = ["%0", "=", "load i32, i32* %a.addr, align 4"]
        # 2) a = ["ret i32 %add", "", ""]
        utils = LlvmParserUtilities()
        if a[1] == '=':
            destination = LlvmName(utils._get_list_element(a, 0))
            source = utils._get_list_element(a, 2)
        return EqualAssignment(destination=destination, source=source)
 
    def get_load_assignment(self, instruction : str) -> AssignmentItem:
        # load i32, i32* %a.addr, align 4
        utils = LlvmParserUtilities()
        c = utils._split_comma(instruction)
        # c = ["load i32", "i32* %a.addr", "align 4"]
        d = utils._split_space(c[1])
        # d = ["i32*", "%a.addr"]
        data_type = LlvmDeclaration(d[0])
        source = LlvmName(d[1])
        # source = "%a.addr"
        return AssignmentItem(source=source, data_type=data_type)

    def get_bitcast_assignment(self, instruction : str) -> AssignmentItem:
        # bitcast [3 x i32]* %n to i8*
        utils = LlvmParserUtilities()
        c = utils._split_space(instruction)
        # c = ["bitcast", "[3", "x", "i32]*", "%n", "to", "i8*"]
        data_type = LlvmDeclaration(c[-4])
        source = LlvmName(c[-3])
        # source = "%n"
        return AssignmentItem(source=source, data_type=data_type)

    def get_getelementptr_assignment(self, instruction : str) -> AssignmentItem:
        self._msg.function_start("get_getelementptr_assignment(instruction=" + instruction + ")")
        # 1) getelementptr inbounds [3 x i32], [3 x i32]* %n, i64 0, i64 0
        # 2) getelementptr inbounds i32, i32* %a, i64 1
        # 3) getelementptr inbounds %struct.StructTest, %struct.StructTest* %x, i64 0, i32 0
        array_index = instruction.rsplit(maxsplit=1)[-1]
        utils = LlvmParserUtilities()
        c = utils._split_comma(instruction)
        # 1) c = ["getelementptr inbounds [3 x i32]", "[3 x i32]* %n", "i64 0", "i64 0"]
        # 2) c = ["getelementptr inbounds i32" , "i32* %a", "i64 1"]
        d = c[1].rsplit(maxsplit=1)
        # 1) d = ["[3 x i32]*", "%n"]
        # 2) d = ["i32*", "%a"]
        data_type = LlvmArrayDeclaration(data_type=d[0], index=array_index)
        source = LlvmName(d[1])
        result = AssignmentItem(source=source, data_type=data_type)
        self._msg.function_end("get_getelementptr_assignment = " + str(result))
        return result

    def get_assignment(self, instruction : str) -> AssignmentItem:
        x = None
        if "load" in instruction:
            x = self.get_load_assignment(instruction)
        elif "bitcast" in instruction:
            x = self.get_bitcast_assignment(instruction)
        elif "getelementptr" in instruction:
            x = self.get_getelementptr_assignment(instruction)
        else:
            raise LlvmParserException("Unknown instruction: " + str(instruction))
        return x

    def get_return_instruction(self, instruction : str) -> ReturnInstruction:
        # ret i32 %add
        # ret void
        utils = LlvmParserUtilities()
        a = utils._remove_empty_elements(instruction.split(' '))
        try:
            value = LlvmName(a[2].strip())
        except IndexError:
            value = None
        data_type = LlvmDeclaration(a[1].strip())
        return ReturnInstruction(value=value, data_type=data_type)
    
    def get_entity_name(self, name: str) -> str:
        return "entity" + name.replace("@", "")


    def get_alloca_assignment(self, instruction: str) -> Alloca:
        # 1) instruction = "alloca [3 x i32], align 4"
        # 2) instruction = "alloca i64, align 8"
        x = instruction.split()
        data_type_position = x[1].replace(",", "")
        data_type = LlvmDeclaration(data_type=data_type_position)
        return Alloca(data_type=data_type)

    def _split_parenthesis(self, text: str) -> Tuple[str, str]:
        self._msg.function_start("_split_parenthesis(text=" + text + ")")
        # text = "call i32 @_Z3addii(i32 2, i32 3)"
        split_text = text.partition('(')
        # split_text = ["call i32 @_Z3addii", "(", "i32 2, i32 3)"]
        head = split_text[0]
        tail = split_text[2].partition(')')[0]
        result = (head, tail)
        self._msg.function_end("_split_parenthesis = " + str(result))
        return result

    def get_call_assignment(self, instruction: str) -> Instruction:
        self._msg.function_start("get_call_assignment(instruction=" + str(instruction) + ")")
        # 1) instruction = "call i32 @_Z3addii(i32 2, i32 3)"
        # 2) instruction = "tail call i32 @_Z3addii(i32 2, i32 3)"
        head, tail = self._split_parenthesis(instruction)
        # 1) head = "call i32 @_Z3addii"
        # 2) head = "tail call i32 @_Z3addii"
        # tail = "i32 2, i32 3"
        head_split = head.split()
        name = self.get_entity_name(head_split[-1])
        data_type = LlvmDeclaration(head_split[-2])
        arguments = LlvmArgumentParser().parse(arguments=tail)
        result = Instruction(library="work", opcode=name, 
                             operands=arguments, data_type=data_type, output_port_name=None)
        self._msg.function_end("get_call_assignment = " + str(result))
        return result

    def _get_type_and_two_arguments_instructions(self) -> Dict[str, InstructionPosition]:
        # 1) fadd float %0, %1
        # 2) or i1 %cmp, %cmp2
        # 3) ashr i32 %a, %b 
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
        # 1) icmp eq i32 %call, 5
        # 2) zext i1 %cmp to i32
        # 3) select i1 %cmp, i32 1, i32 2
        # 4) trunc i64 %x.coerce to i32
        # 5) store i32 %a, i32* %a.addr, align 4
        position: dict = {
            "icmp": InstructionPosition(opcode=1, data_type=2, operands=[(2, 3), (2, 4)]),
            "zext": InstructionPosition(opcode=0, data_type=1, operands=[(1, 2)]),
            "trunc": InstructionPosition(opcode=0, data_type=4, operands=[(1, 2)]),
            "select": InstructionPosition(opcode=0, data_type=3, operands=[(1, 2), (3, 4), (5, 6)]),
            "store": InstructionPosition(opcode=0, data_type=1, operands=[(1, 2), (3, 4)])}
        return position

    def _get_instruction_positions(self) -> Dict[str, InstructionPosition]:
        dict_1 = self._get_type_and_two_arguments_instructions()
        dict_2 = self._get_arithmetic_instructions()
        dict_3 = self._get_special_instructions()
        return dict_1 | dict_2 | dict_3

    def get_instruction(self, instruction: str) -> Instruction:
        self._msg.function_start("get_instruction(instruction=" + instruction + ")")
        utils = LlvmParserUtilities()
        a = utils._split_space(instruction)
        position: Dict[str, InstructionPosition] = self._get_instruction_positions()
        opcode = utils._get_list_element(a, 0)
        x = InstructionParser(instruction=a, position=position[opcode])
        result = Instruction(library="llvm", opcode="llvm_" + x.opcode, 
        operands=x.operands, data_type=LlvmDeclaration(x.data_type), output_port_name="m_tdata")
        self._msg.function_end("get_instruction = " + str(result))
        return result

    def _remove_comments(self, text: str) -> str:
        line_starting_with_semicolon = r';.*'
        return re.sub(line_starting_with_semicolon, '', text)

    def _findall(self, text: str, regex: str) -> List[str]:
        matches = re.finditer(regex, text, re.MULTILINE)
        result = [match.group() for match in matches]
        return result

    def _extract_functions(self, text: str) -> List[str]:
        self._msg.function_start("text=" + text)
        match_word_define = r"define "
        all_characters_including_newline = r"(.|\n)*"
        until_right_bracket = r"?\}"
        regex = match_word_define + all_characters_including_newline + until_right_bracket
        result = self._findall(text=text, regex=regex)
        self._msg.function_end(result)
        return result

    def _extract_constants(self, text: str) -> List[str]:
        self._msg.function_start("text=" + str(text), True)
        """
        @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
        """
        lines = text.split("\n")
        result = [i for i in lines if i.startswith("@")]
        self._msg.function_end(result, True)
        return result

    def parse(self, text: str) -> LlvmModule:
        self._msg.function_start("text=" + text)
        without_comments = self._remove_comments(text)
        functions = self._extract_functions(without_comments)
        constants = self._extract_constants(without_comments)
        llvm_functions =[LlvmFunctionParser().parse(i) for i in functions]
        llvm_constants = [LlvmConstantParser().parse(i) for i in constants]
        llvm_module = LlvmModule(functions=llvm_functions, constants=llvm_constants)
        self._msg.function_end(llvm_module)
        return llvm_module