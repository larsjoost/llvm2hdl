from typing import List
from llvmlite.binding import ValueRef

from dataclasses import dataclass
from file_writer import FileWriter
from instance_statistics import InstanceStatistics
from llvm_parser import Assignment, LlvmParser, Instruction
from messages import Messages
from vhdl_declarations import VhdlDeclarations
from llvm_declarations import LlvmDeclarations

class Instance:

    instruction: Instruction

    def __init__(self, parent):
        self.parent = parent
        self.library = "llvm"
        self.next = None
        self.prev = None
        self.llvm_decl = LlvmDeclarations()
        self.vhdl_decl = VhdlDeclarations()
        self.llvm_parser = LlvmParser()

    def setInstruction(self, instruction : Instruction):
        self.instruction = instruction

    def getDataWidth(self):
        return self.instruction.data_width

    def getInstanceIndex(self) -> int:
        if self.prev is None:
            return 1
        return self.prev.getInstanceIndex() + 1

    def _get_component_name(self, opcode: str) -> str:
        return "llvm_" + opcode

    def getInstanceName(self) -> str:
        return "inst_" + self._get_component_name(self.instruction.opcode) + "_" + str(self.getInstanceIndex())

    def getTagName(self) -> str:
        return self.getInstanceName() + "_tag_out_i"

    def getInstanceTagName(self, instance, default: str) -> str:
        if instance is None:
            return default
        return instance.getTagName()	

    def getPreviousTagName(self) -> str:
        return self.getInstanceTagName(self.prev, "tag_in")	

    def getNextTagName(self) -> str:
        return self.getInstanceTagName(self.next, "tag_out")	

    def getOutputSignalName(self) -> str:
        instance_name = self.getInstanceName()
        return instance_name + "_q_i"

    def write_instance(self, file_handle: FileWriter):
        instance_name = self.getInstanceName()
        file_handle.write(instance_name + " : entity " + self.library + "." + self._get_component_name(self.instruction.opcode))
        input_ports = ""
        for index, operand in enumerate(self.instruction.operands):
            input_ports += ", " + chr(ord('a') + index) + " => " + str(self.parent.getSource(operand))
        file_handle.write("port map (clk => clk, sreset => sreset", end="")
        file_handle.write(", tag_in => " + self.getPreviousTagName(), end="")
        file_handle.write(input_ports, end="")
        file_handle.write(", tag_out => " + self.getNextTagName(), end="")
        file_handle.write(", q => " + self.getOutputSignalName(), end="")
        file_handle.write(");")	

    def write_declarations(self, file_handle):
        file_handle.write("signal ", end="")
        file_handle.write(self.getOutputSignalName(), end="")
        file_handle.write(" : ", end="")
        file_handle.write(self.vhdl_decl.get_type_declarations(self.getDataWidth()), end="")
        file_handle.write(';')

class InstanceContainer:
    
    _container: List[Instance]
    _return_value: str

    def __init__(self):
        self._msg = Messages()
        self._llvm_parser = LlvmParser()
        self._container = []
        self._assignment_map = {}
        self._instance_map = {}

    def resolveAssignment(self, assignment: str) -> List[str]:
        if assignment in self._assignment_map:
            return self.resolveAssignment(self._assignment_map[assignment])
        return assignment

    def _resolveSource(self, operand):
        x = self.getAssignment(str(operand))
        return self.resolveAssignment(x.destination)

    def getSource(self, operand):
        x = self.resolveAssignment(operand)
        return x[1:] if x[0] == "%" else x

    def _add_instruction(self, destination : str, instruction : Instruction):
        instance = Instance(self)
        try:
            last_instance = self._container[-1]
            last_instance.next = instance
            instance.prev = last_instance
        except IndexError:
            pass
        instance.setInstruction(instruction)
        self._instance_map[destination] = instance
        self._container.append(instance)

    def getAssignment(self, instruction : str):
        return self._llvm_parser.get_assignment(instruction)

    def _add_call_instruction(self, instruction: str):
        x = self._llvm_parser.get_call_assignment(instruction)
        self._msg.note(str(instruction))

    def _addAssignmentInstruction(self, instruction: str):
        x = self.getAssignment(instruction)
        self._assignment_map[x.destination] = x.source

    def _add_return_instruction(self, instruction: str) -> str:
        self._msg.function_start("add_return_instruction(instruction=" + str(instruction) + ")", True)
        return_instruction = self._llvm_parser.get_return_instruction(instruction)
        result = self._instance_map[return_instruction.value].getOutputSignalName()
        self._msg.function_end("_add_return_instruction = " + str(result), True)
        return result

    def add_instruction(self, instruction: ValueRef, statistics: InstanceStatistics):
        self._msg.function_start("add_instruction(instruction=" + str(instruction) + ")", True)
        if instruction.opcode in ["add", "sub", "mul", "fadd", "icmp", "xor", "zext"]:
            statistics.increment(instruction.opcode)
            x: Assignment = self._llvm_parser.get_equal_assignment(str(instruction))
            a: Instruction = self._llvm_parser.get_instruction(x.source)
            self._add_instruction(x.destination, a)
        elif instruction.opcode == "call":
            x: Assignment = self._llvm_parser.get_equal_assignment(str(instruction))
            self._add_call_instruction(x.source)
        elif instruction.opcode in ["store", "load"]:
            self._addAssignmentInstruction(str(instruction))
        elif instruction.opcode == "ret":
            self._return_value = self._add_return_instruction(str(instruction))
        elif instruction.opcode == "alloca":
            pass
        else:
            self._msg.error("Unknown instruction: " + str(instruction.opcode) + " (" + str(instruction) + ")")
        self._msg.function_end("add_instruction", True)

    def write_instances(self, file_handle):
        self._msg.function_start("write_instance()", True)
        for i in self._container:
            i.write_instance(file_handle)
        file_handle.write("return_value <= " + str(self._return_value) + ";")
        self._msg.function_end("write_instance")

    def write_declarations(self, file_handle):
        for i in self._container:
            i.write_declarations(file_handle)
            