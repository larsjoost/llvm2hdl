from dataclasses import dataclass
from typing import List, Tuple, Optional, Union

from messages import Messages
from llvm_declarations import LlvmDeclarations
from vhdl_declarations import VhdlDeclarations

@dataclass
class InstructionPosition:
    opcode: int
    operands: List[int]
    data_type: int

@dataclass
class InstructionArgument:
    signal_name: str
    data_width : int
    port_name: Optional[str] = None
    def get_port_map(self) -> str:
        result = "conv_std_ulogic_vector(" + self.signal_name + ", " + str(self.data_width) + ")"
        if self.port_name is not None:
            result = self.port_name + " => " + result
        return result

@dataclass
class OutputPort:
    data_width : int
    port_name: Optional[str] = None
    def get_type_declarations(self) -> str:
        return VhdlDeclarations(data_width=self.data_width).get_type_declarations()
    def get_port_map(self) -> str:
        port_map = "q_i"
        if self.port_name is not None:
            port_map = self.port_name + " => " + port_map
        return port_map

class InstructionParser:
    source : str
    opcode : str
    operands : List[str]
    data_type : str
    def __init__(self, instruction: List[str], position: InstructionPosition):
        self.source = instruction
        self.opcode = instruction[position.opcode]
        self.data_type = instruction[position.data_type]
        self.operands = [self._parse_operand(instruction[item], index) for index, item in enumerate(position.operands)]
    def _parse_operand(self, operand: str, index: int) -> InstructionArgument:
        signal_name = operand.replace(",", "")
        port_name = chr(ord('a') + index)
        data_width = LlvmDeclarations(self.data_type).get_data_width()
        return InstructionArgument(port_name=port_name, signal_name=signal_name, data_width=data_width)
    def __str__(self) -> str:
        return str(vars(self))

@dataclass
class Instruction:
    source : str
    library: str
    opcode: str
    operands: List[InstructionArgument]
    data_type: LlvmDeclarations
    output_port_name: str
    def get_output_port(self) -> OutputPort:
        return OutputPort(data_width=self.get_data_width(), port_name=self.output_port_name)
    def get_data_width(self) -> int:
        return self.data_type.get_data_width()

class LlvmParserException(Exception):
    pass

@dataclass
class Assignment:
    destination : Optional[str]
    source : str
    
@dataclass
class ReturnInstruction:
    value : str
    data_type : str
    data_width : int
    
@dataclass
class Alloca:
    size : int
    data_type : str

class LlvmParser:

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

    def get_equal_assignment(self, instruction : str) -> Assignment:
        # 1) instruction = "%0 = load i32, i32* %a.addr, align 4"
        # 2) instruction = "ret i32 %add"
        source: str = instruction
        destination: Optional[str] = None
        a: Tuple[str, str, str] = source.partition('=')
        # 1) a = ["%0", "=", "load i32, i32* %a.addr, align 4"]
        # 2) a = ["ret i32 %add", "", ""]
        if a[1] == '=':
            destination = self._get_list_element(a, 0)
            source = self._get_list_element(a, 2)
        return Assignment(destination=destination, source=source)
 
    def get_store_assignment(self, instruction : str) -> Assignment:
        # store i32 %a, i32* %a.addr, align 4
        a = self._split_comma(instruction)
        # a = ["store i32 %a", "i32* %a.addr", "align 4"]
        b = self._split_space(a[0])
        # b = ["store", "i32", "%a"]
        source = self._get_list_element(b, 2)
        # source = "%a"
        b = self._split_space(a[1])
        # b = ["i32*", "%a.addr"]
        destination = b[1]
        # destination = "%a.addr"
        return Assignment(destination=destination, source=source)

    def get_load_assignment(self, instruction : str) -> Assignment:
        # %0 = load i32, i32* %a.addr, align 4
        a = self._split_equal_sign(instruction)
        # a = ["%0", "load i32, i32* %a.addr, align 4"]
        destination = self._get_list_element(a, 0)
        # destination = "%0"
        c = self._split_comma(a[1])
        # c = ["load i32", "i32* %a.addr", "align 4"]
        d = self._split_space(c[1])
        # d = ["i32*", "%a.addr"]
        source = d[1]
        # source = "%a.addr"
        return Assignment(destination=destination, source=source)

    def get_bitcast_assignment(self, instruction : str) -> Assignment:
        # %0 = bitcast [3 x i32]* %n to i8*
        a = self._split_equal_sign(instruction)
        # a = ["%0", "bitcast [3 x i32]* %n to i8*"]
        destination = self._get_list_element(a, 0)
        # destination = "%0"
        c = self._split_space(a[1])
        # c = ["bitcast", "[3", "x", "i32]*", "%n", "to", "i8*"]
        source = c[-3]
        # source = "%n"
        return Assignment(destination=destination, source=source)

    def get_getelementptr_assignment(self, instruction : str) -> Assignment:
        # %arraydecay = getelementptr inbounds [3 x i32], [3 x i32]* %n, i64 0, i64 0
        a = self._split_equal_sign(instruction)
        # a = ["%arraydecay", "getelementptr inbounds [3 x i32], [3 x i32]* %n, i64 0, i64 0"]
        destination = self._get_list_element(a, 0)
        # destination = "%0"
        c = self._split_comma(a[1])
        # c = ["getelementptr inbounds [3 x i32]", "[3 x i32]* %n", "i64 0", "i64 0"]
        d = self._split_space(c[-3])
        # c = ["[3", "x", "i32]*", "%n"]
        source = d[-1]
        # source = "%n"
        return Assignment(destination=destination, source=source)

    def get_assignment(self, instruction : str) -> Optional[Assignment]:
        x = None
        if "store" in instruction:
            x = self.get_store_assignment(instruction)
        elif "load" in instruction:
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
        a = self._remove_empty_elements(instruction.split(' '))
        value = a[2].strip()
        data_type = a[1].strip()
        data_width = LlvmDeclarations(data_type).get_data_width()
        return ReturnInstruction(value=value, data_type=data_type, data_width=data_width)
    
    def get_entity_name(self, name: str) -> str:
        return "entity" + name.replace("@", "")

    def _get_call_arguments(self, arguments: str) -> List[InstructionArgument]:
        # arguments = "i32 2, i32* nonnull %n"
        result = []
        for i in self._split_comma(arguments):
            # 1) i = "i32 2"
            # 2) i = "i32* nonnull %n"
            g = self._split_space(i) 
            # 1) g = ["i32", "2"]
            # 2) b = ["i32*", "nonnull",  "%n"]
            data_width = LlvmDeclarations(self._get_list_element(g, 0))
            signal_name = self._get_list_element(g, -1)
            # 1) signal_name = "2"
            # 2) signal_name = "%n"
            result.append(InstructionArgument(signal_name=signal_name, data_width=data_width))
        return result

    def _get_within(self, text: str, left: str, right: str) -> str:
        # text = alloca [3 x i32], align 4
        split_text = text.partition(left)
        # split_text = ["alloca ", "[", "3 x i32], align 4"]
        within = split_text[2].partition(right)
        # within = ["3 x i32", "]", ",align 4"]
        return within[0]

    def get_alloca_assignment(self, instruction: str) -> Alloca:
        # instruction = "alloca [3 x i32], align 4"
        dimension = self._get_within(instruction, "[", "]")
        # dimension = "3 x i32"
        dimension_elements = dimension.partition("x")
        # dimension_elements = ["3", "x", "i32"]
        size = int(dimension_elements[0])
        data_type = dimension_elements[2]
        return Alloca(size=size, data_type=data_type)

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
        data_type = LlvmDeclarations(head_split[-2])
        arguments = self._get_call_arguments(arguments=tail)
        result = Instruction(source=instruction, library="work", opcode=name, 
        operands=arguments, data_type=data_type, output_port_name=None)
        self._msg.function_end("get_call_assignment = " + str(result))
        return result

    def get_instruction(self, instruction: str) -> Instruction:
        self._msg.function_start("get_instruction(instruction=" + instruction + ")")
        # 1) add nsw i32 %0, %1
        # 2) fadd float %0, %1
        # 3) icmp eq i32 %call, 5
        # 4) zext i1 %cmp to i32
        a = self._split_space(instruction)
        position: dict = {
            "add": InstructionPosition(opcode=0, data_type=2, operands=[3, 4]),
            "sub": InstructionPosition(opcode=0, data_type=2, operands=[3, 4]),
            "mul": InstructionPosition(opcode=0, data_type=2, operands=[3, 4]),
            "fadd": InstructionPosition(opcode=0, data_type=1, operands=[2, 3]),
            "icmp": InstructionPosition(opcode=1, data_type=2, operands=[3, 4]),
            "xor": InstructionPosition(opcode=0, data_type=1, operands=[2, 3]),
            "zext": InstructionPosition(opcode=0, data_type=1, operands=[2])}
        opcode = self._get_list_element(a, 0)
        instruction = InstructionParser(instruction=a, position=position[opcode])
        result = Instruction(source=instruction.source, library="llvm", opcode="llvm_" + instruction.opcode, 
        operands=instruction.operands, data_type=LlvmDeclarations(instruction.data_type), output_port_name="q")
        self._msg.function_end("get_instruction = " + str(result))
        return result