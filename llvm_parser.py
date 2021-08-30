from dataclasses import dataclass

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

class LlvmParser:

    def __init__(self):
        self.msg = Messages()
        self.llvm_decl = LlvmDeclarations()

    def _removeEmptyElements(self, x):
        return [i for i in x if len(i) > 0]

    def split(self, x, split_char):
        return self._removeEmptyElements(x.split(split_char))

    def splitEqualSign(self, x):
        return self.split(x, '=')

    def splitSpace(self, x):
        return self.split(x, ' ')

    def splitComma(self, x):
        return self.split(x, ',')

    def getListElement(self, x : list, index : int):
        return x[index].strip()

    def removeFirstWord(self, x : str) -> str:
        return x.strip().partition(' ')[2]

    @dataclass
    class Assignment:
        destination : str
        source : str

    def getEqualAssignment(self, instruction : str):
        # 1) instruction = "%0 = load i32, i32* %a.addr, align 4"
        # 2) instruction = "ret i32 %add"
        source = instruction
        destination = None
        a = source.partition('=')
        # 1) a = ["%0", "=", "load i32, i32* %a.addr, align 4"]
        # 2) a = ["ret i32 %add", "", ""]
        if a[1] == '=':
            destination = self.getListElement(a, 0)
            source = self.getListElement(a, 2)
        return self.Assignment(destination=destination, source=source)

 
    def getStoreAssignment(self, instruction : str):
        # store i32 %a, i32* %a.addr, align 4
        a = self.splitComma(instruction)
        # a = ["store i32 %a", "i32* %a.addr", "align 4"]
        b = self.splitSpace(a[0])
        # b = ["store", "i32", "%a"]
        source = self.getListElement(b, 2)
        # source = "%a"
        b = self.splitSpace(a[1])
        # b = ["i32*", "%a.addr"]
        destination = b[1]
        # destination = "%a.addr"
        return self.Assignment(destination=destination, source=source)

    def getLoadAssignment(self, instruction : str):
        # %0 = load i32, i32* %a.addr, align 4
        a = self.splitEqualSign(instruction)
        # a = ["%0", "load i32, i32* %a.addr, align 4"]
        destination = self.getListElement(a, 0)
        # destination = "%0"
        c = self.splitComma(a[1])
        # c = ["load i32", "i32* %a.addr", "align 4"]
        d = self.splitSpace(c[1])
        # d = ["i32*", "%a.addr"]
        source = d[1]
        # source = "%a.addr"
        return self.Assignment(destination=destination, source=source)

    def getAssignment(self, instruction : str):
        x = None
        if "store" in instruction:
            x = self.getStoreAssignment(instruction)
        elif "load" in instruction:
            x = self.getLoadAssignment(instruction)
        else:
            raise LlvmParserException("Unknown instruction: " + str(instruction))
        return x

    @dataclass
    class ReturnInstruction:
        value : str
        data_type : str
        data_width : int

    def getReturnInstruction(self, instruction : str):
        # ret i32 %add
        a = self._removeEmptyElements(instruction.split(' '))
        value = a[2].strip()
        data_type = a[1].strip()
        data_width = self.llvm_decl.getDataWidth(data_type) 
        return self.ReturnInstruction(value=value, data_type=data_type, data_width=data_width)
        
    @dataclass
    class CallAssignment:
        reference : str
        name : str
        arguments : list

    def getCallAssignment(self, instruction):
        # instruction = "%call = call i32 @_Z3addii(i32 2, i32 3)"
        a = self.splitEqualSign(instruction)
        # a = ["%call", "call i32 @_Z3addii(i32 2, i32 3)"]
        reference = self.getListElement(a, 0)
        # reference = "%call"
        b = self.removeFirstWord(self.getListElement(a, 1))
        # b = "i32 @_Z3addii(i32 2, i32 3)"
        c = self.removeFirstWord(b)
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
        for i in self.splitComma(f):
            # i = "i32 2"
            g = self.splitSpace(i) 
            # g = ["i32", "2"]
            h = self.getListElement(g, 1)
            # h = "2"
            arguments.append(h)
        return self.CallAssignment(reference=reference, name=name, arguments=arguments)
 

    def getInstruction(self, instruction):
        # add nsw i32 %0, %1
        a = self.splitSpace(instruction)
        # a = ["add", "nsw", "i32", "%0,", "%1"]
        opcode = self.getListElement(a, 0)
        # opcode = "add"
        data_type = self.getListElement(a, 2)
        # data_type = "i32"
        data_width = self.llvm_decl.getDataWidth(data_type) 
        # data_width = 32
        operands = [self.getListElement(a, 3).replace(',', ''), self.getListElement(a, 4).replace(',', '')]
        return Instruction(source=instruction, opcode=opcode, operands=operands, data_type=data_type, data_width=data_width)
