from dataclasses import dataclass
from typing import List, Tuple, Optional, Union

from messages import Messages
from llvm_declarations import LlvmDeclarations

@dataclass
class Instruction:
    source : str
    opcode : str
    operands : list
    data_type : str
    data_width : int

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
class CallAssignment:
    reference : str
    name : str
    arguments : list

class LlvmParser:

    def __init__(self):
        self._msg = Messages()
        self.llvm_decl = LlvmDeclarations()

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
        self._msg.function_start("_get_list_element(x=" + str(x) + ", index=" + str(index), True)
        result = x[index].strip()
        self._msg.function_end("_get_list_element = " + str(result), True)
        return result

    def _remove_first_word(self, x : str) -> str:
        return x.strip().partition(' ')[2]

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

    def get_assignment(self, instruction : str) -> Optional[Assignment]:
        x = None
        if "store" in instruction:
            x = self.get_store_assignment(instruction)
        elif "load" in instruction:
            x = self.get_load_assignment(instruction)
        else:
            raise LlvmParserException("Unknown instruction: " + str(instruction))
        return x

    def get_return_instruction(self, instruction : str) -> ReturnInstruction:
        # ret i32 %add
        a = self._remove_empty_elements(instruction.split(' '))
        value = a[2].strip()
        data_type = a[1].strip()
        data_width = self.llvm_decl.get_data_width(data_type)
        return ReturnInstruction(value=value, data_type=data_type, data_width=data_width)
    
    def get_call_assignment(self, instruction: str) -> CallAssignment:
        self._msg.function_start("get_call_assignment(instruction=" + str(instruction) + ")", True)
        # 1) instruction = "%call = call i32 @_Z3addii(i32 2, i32 3)"
        # 2) instruction = "call i32 @_Z3addii(i32 2, i32 3)"
        if "=" in instruction:
            a = self._split_equal_sign(instruction)
            reference = self._get_list_element(a, 0)
            # reference = "%call"
            # a = ["%call", "call i32 @_Z3addii(i32 2, i32 3)"]
            a = self._get_list_element(a, 1)
        else:
            a = instruction
            reference = None
        b = self._remove_first_word(a)
        # b = "i32 @_Z3addii(i32 2, i32 3)"
        c = self._remove_first_word(b)
        # c = "@_Z3addii(i32 2, i32 3)"
        d = c.partition('(')
        # d = ["@_Z3addii", "(", "i32 2, i32 3)"]
        name = d[0]
        # name = "@_Z3addii"
        e = d[2].partition(')')
        # e = ["i32 2, i32 3", ")", ""]
        f = e[0]
        # f = "i32 2, i32 3"
        arguments = []
        for i in self._split_comma(f):
            # i = "i32 2"
            g = self._split_space(i) 
            # g = ["i32", "2"]
            h = self._get_list_element(g, 1)
            # h = "2"
            arguments.append(h)
        result = CallAssignment(reference=reference, name=name, arguments=arguments)
        self._msg.function_end("get_call_assignment = " + str(result), True)
        return result

    def get_instruction(self, instruction: str) -> Instruction:
        # 1) add nsw i32 %0, %1
        # 2) fadd float %0, %1
        # 3) icmp eq i32 %call, 5
        # 4) zext i1 %cmp to i32
        a = self._split_space(instruction)
        # 1) a = ["add", "nsw", "i32", "%0,", "%1"]
        # 2) a = ["fadd", "float", "%0,", "%1"]
        # 3) a = ["icmp", "eq", "i32", "%call", "5"]
        # 4) a = ["zext", "i1" , "%cmp", "to", "i32"]
        opcode = self._get_list_element(a, 0)
        opcode_position: dict = {"icmp": 1}
        if opcode in opcode_position:
            opcode = a[opcode_position[opcode]]
        # 1) opcode = "add"
        # 2) opcode = "fadd"
        # 3) opcode = "eq"
        # 4) opcode = "zext"
        operand_position: dict = {"add": 2, "fadd": 1, "eq": 2, "ne": 2, "xor": 1, "zext": 1}
        position = operand_position[opcode]
        a = a[position:]
        # 1) a = ["i32", "%0,", "%1"]
        # 2) a = ["float", "%0,", "%1"]
        # 3) a = ["i32", "%call,", "5"]
        # 4) a = ["i1", "%cmp,", "to", "i32"]
        data_type: str = self._get_list_element(a, 0)
        # data_type = "i32"
        data_width: int = self.llvm_decl.get_data_width(data_type)
        # data_width = 32
        operands_position = {"zext": range(1, 1)}
        operands_range = operands_position.get(opcode, range(1, 2))
        operands = [self._get_list_element(a, i).replace(',', '') for i in operands_range]
        return Instruction(source=instruction, opcode=opcode,
        operands=operands, data_type=data_type, data_width=data_width)
