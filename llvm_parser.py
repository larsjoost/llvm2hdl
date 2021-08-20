from dataclasses import dataclass

from messages import Messages
from llvm_declarations import LlvmDeclarations

class LlvmParser:

    def __init__(self):
        self.msg = Messages()
        self.llvm_decl = LlvmDeclarations()

    def _removeEmptyElements(self, x):
        return [i for i in x if len(i) > 0]

    @dataclass
    class Assignment:
        destination : str
        source : str

    def getAssignment(self, instruction : str):
        x = None
        if "store" in instruction:
			# store i32 %a, i32* %a.addr, align 4
            a = instruction.split(',')
            b = a[0].split(' ')
            source = self._removeEmptyElements(b)[2].strip()
            b = a[1].split(' ')
            destination = self._removeEmptyElements(b)[1].strip()
            x = self.Assignment(destination=destination, source=source)
        elif "load" in instruction:
            # %0 = load i32, i32* %a.addr, align 4
            a = instruction.split('=')
            destination = self._removeEmptyElements(a)[0].strip()
            c = a[1].split(',')
            d = c[1].split(' ')
            source = self._removeEmptyElements(d)[1].strip()
            x = self.Assignment(destination=destination, source=source)
        else:
            self.msg.error("Unknown instruction: " + str(instruction))
        return x

    @dataclass
    class ReturnInstruction:
        value : str
        data_type : str
        data_width : int

    def getReturnInstruction(self, instruction):
        # ret i32 %add
        a = self._removeEmptyElements(str(instruction).split(' '))
        value = a[2].strip()
        data_type = a[1].strip()
        data_width = self.llvm_decl.getDataWidth(data_type) 
        x = self.ReturnInstruction(value=value, data_type=data_type, data_width=data_width)
        self.msg.debug("Parsing return instruction: " + str(instruction) + " : " + str(x))
        return x

    @dataclass
    class Instruction:
        opcode : str
        operand1 : str
        operand2 : str
        data_type : str
        data_width : int

    def getInstruction(self, instruction):
        # %add = add nsw i32 %0, %1
        a = self._removeEmptyElements(str(instruction).split("="))
        opcode = a[0].strip()
        after_equal_char = self._removeEmptyElements(a[1].split(' '))
        data_type = after_equal_char[2].strip()
        data_width = self.llvm_decl.getDataWidth(data_type) 
        operand1 = after_equal_char[3].strip()
        operand2 = after_equal_char[4].strip()
        return self.Instruction(opcode=opcode, operand1=operand1, operand2=operand2, data_type=data_type, data_width=data_width)
