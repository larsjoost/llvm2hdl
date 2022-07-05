from dataclasses import dataclass
from typing import List, Tuple, Optional, Union
from assignment_resolution import AssignmentItem

from messages import Messages
from llvm_declarations import LlvmArrayDeclaration, LlvmDeclaration, LlvmName, LlvmType, LlvmTypeFactory
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
        return self.name.split(".")[-1]
    def get_dimensions(self) -> Tuple[int, int]:
        return self.type.get_dimensions()
    def get_values(self) -> List[str]:
        return [i.value for i in self.values]

@dataclass
class InstructionPosition:
    opcode: int
    operands: List[int]
    data_type: int

@dataclass
class InstructionArgument:
    signal_name: Union[str, LlvmType]
    data_type : LlvmDeclaration
    port_name: Optional[str] = None
    def get_dimensions(self) -> Tuple[int, int]:
        return self.data_type.get_dimensions()
    def single_dimension(self) -> bool:
        return self.data_type.single_dimension()
    def is_pointer(self) -> bool:
        return self.data_type.is_pointer()
    def get_array_index(self) -> str:
        return self.data_type.get_array_index()
    def is_integer(self) -> bool:
        if isinstance(self.signal_name, LlvmType):
            return self.signal_name.is_integer()
        return False
    def get_reference_arguments(self) -> Tuple[str, Optional[str]]:
        return self.data_type.get_reference_arguments()

@dataclass
class OutputPort:
    data_type : LlvmDeclaration
    port_name: Optional[str] = None
    def get_type_declarations(self) -> str:
        return VhdlDeclarations(self.data_type).get_type_declarations()
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
        signal_name = LlvmTypeFactory(operand.replace(",", "")).resolve()
        port_name = chr(ord('a') + index)
        data_type = LlvmDeclaration(self.data_type)
        return InstructionArgument(port_name=port_name, signal_name=signal_name, data_type=data_type)
    def __str__(self) -> str:
        return str(vars(self))

@dataclass
class Instruction:
    source : str
    library: str
    opcode: str
    operands: List[InstructionArgument]
    data_type: LlvmDeclaration
    output_port_name: str
    def get_output_port(self) -> OutputPort:
        return OutputPort(data_type=self.data_type, port_name=self.output_port_name)

class LlvmParserException(Exception):
    pass

@dataclass
class EqualAssignment:
    destination : LlvmName
    source : str

    
@dataclass
class ReturnInstruction:
    value : LlvmName
    data_type : LlvmDeclaration
    
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

    def get_equal_assignment(self, instruction : str) -> EqualAssignment:
        # 1) instruction = "%0 = load i32, i32* %a.addr, align 4"
        # 2) instruction = "ret i32 %add"
        source: str = instruction
        destination: Optional[str] = None
        a: Tuple[str, str, str] = source.partition('=')
        # 1) a = ["%0", "=", "load i32, i32* %a.addr, align 4"]
        # 2) a = ["ret i32 %add", "", ""]
        if a[1] == '=':
            destination = LlvmName(self._get_list_element(a, 0))
            source = self._get_list_element(a, 2)
        return EqualAssignment(destination=destination, source=source)
 
    def get_store_assignment(self, instruction : str) -> Tuple[LlvmName, AssignmentItem]:
        # store i32 %a, i32* %a.addr, align 4
        a = self._split_comma(instruction)
        # a = ["store i32 %a", "i32* %a.addr", "align 4"]
        b = self._split_space(a[0])
        # b = ["store", "i32", "%a"]
        source = LlvmName(self._get_list_element(b, 2))
        # source = "%a"
        b = self._split_space(a[1])
        # b = ["i32*", "%a.addr"]
        data_type = LlvmDeclaration(b[0])
        destination = LlvmName(b[1])
        # destination = "%a.addr"
        return (destination, AssignmentItem(source=source, data_type=data_type))

    def get_load_assignment(self, instruction : str) -> AssignmentItem:
        # load i32, i32* %a.addr, align 4
        c = self._split_comma(instruction)
        # c = ["load i32", "i32* %a.addr", "align 4"]
        d = self._split_space(c[1])
        # d = ["i32*", "%a.addr"]
        data_type = LlvmDeclaration(d[0])
        source = LlvmName(d[1])
        # source = "%a.addr"
        return AssignmentItem(source=source, data_type=data_type)

    def get_bitcast_assignment(self, instruction : str) -> AssignmentItem:
        # bitcast [3 x i32]* %n to i8*
        c = self._split_space(instruction)
        # c = ["bitcast", "[3", "x", "i32]*", "%n", "to", "i8*"]
        data_type = LlvmDeclaration(c[-4])
        source = LlvmName(c[-3])
        # source = "%n"
        return AssignmentItem(source=source, data_type=data_type)

    def get_getelementptr_assignment(self, instruction : str) -> AssignmentItem:
        self._msg.function_start("get_getelementptr_assignment(instruction=" + instruction + ")")
        # 1) getelementptr inbounds [3 x i32], [3 x i32]* %n, i64 0, i64 0
        # 2) getelementptr inbounds i32, i32* %a, i64 1
        array_index = instruction.rsplit(maxsplit=1)[-1]
        c = self._split_comma(instruction)
        # 1) c = ["getelementptr inbounds [3 x i32]", "[3 x i32]* %n", "i64 0", "i64 0"]
        # 2) c = ["getelementptr inbounds i32" , "i32* %a", "i64 1"]
        d = c[1].rsplit(maxsplit=1)
        # 1) d = ["[3 x i32]*", "%n"]
        # 2) d = ["i32*", "%a"]
        data_type = LlvmArrayDeclaration(data_type=LlvmDeclaration(d[0]), index=array_index)
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
        a = self._remove_empty_elements(instruction.split(' '))
        value = LlvmName(a[2].strip())
        data_type = LlvmDeclaration(a[1].strip())
        return ReturnInstruction(value=value, data_type=data_type)
    
    def get_entity_name(self, name: str) -> str:
        return "entity" + name.replace("@", "")

    def _get_call_arguments(self, arguments: str) -> List[InstructionArgument]:
        self._msg.function_start("_get_call_argument(arguments=" + arguments + ")")
        # arguments = "i32 2, i32* nonnull %n"
        result = []
        for i in self._split_comma(arguments):
            # 1) i = "i32 2"
            # 2) i = "i32* nonnull %n"
            g = self._split_space(i) 
            # 1) g = ["i32", "2"]
            # 2) b = ["i32*", "nonnull",  "%n"]
            data_type = LlvmDeclaration(self._get_list_element(g, 0))
            argument = LlvmTypeFactory(self._get_list_element(g, -1)).resolve()
            # 1) signal_name = "2"
            # 2) signal_name = "%n"
            result.append(InstructionArgument(signal_name=argument, data_type=data_type))
        self._msg.function_end("_get_call_argument = " + str(result))
        return result

    def _get_within(self, text: str, left: str, right: str) -> str:
        # text = alloca [3 x i32], align 4
        split_text = text.partition(left)
        # split_text = ["alloca ", "[", "3 x i32], align 4"]
        within = split_text[2].partition(right)
        # within = ["3 x i32", "]", ",align 4"]
        return within[0]

    def get_constant_declaration(self, instruction: str) -> ConstantDeclaration:
        # @__const.main.n = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4
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
        return ConstantDeclaration(name=name, type=type, values=definitions)

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
        data_type = LlvmDeclaration(head_split[-2])
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
        operands=instruction.operands, data_type=LlvmDeclaration(instruction.data_type), output_port_name="q")
        self._msg.function_end("get_instruction = " + str(result))
        return result