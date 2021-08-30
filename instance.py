from dataclasses import dataclass
from llvm_parser import LlvmParser
from llvm_parser import Instruction
from messages import Messages
from vhdl_declarations import VhdlDeclarations
from llvm_declarations import LlvmDeclarations


class Instance:
	
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

	def getInstanceIndex(self):
		if self.prev is None:
			return 1
		return self.prev.getInstanceIndex() + 1

	def getInstanceName(self):
		return "inst_" + self.instruction.opcode + "_" + str(self.getInstanceIndex())
		
	def getTagName(self):
		return self.getInstanceName() + "_tag_out_i"

	def getInstanceTagName(self, instance, default):
		if instance is None:
			return default
		return instance.getTagName()	

	def getPreviousTagName(self):
		return self.getInstanceTagName(self.prev, "tag_in")	

	def getNextTagName(self):
		return self.getInstanceTagName(self.next, "tag_out")	

	def getOutputSignalName(self):
		instance_name = self.getInstanceName()
		return instance_name + "_q_i"

	def writeInstance(self, file_handle):
		instance_name = self.getInstanceName()
		file_handle.write(instance_name + " : entity " + self.library + "." + self.instruction.opcode + " is ")
		input_ports = ""
		for index, operand in enumerate(self.instruction.operands):
			input_ports += ", " + chr(ord('a') + index) + " => " + str(self.parent.getSource(operand))
		file_handle.write("port map (clk => clk, sreset => sreset")
		file_handle.write(", tag_in => " + self.getPreviousTagName())
		file_handle.write(input_ports)
		file_handle.write(", tag_out => " + self.getNextTagName())
		file_handle.write(", q => " + self.getOutputSignalName())
		file_handle.write(");\n")	

	def writeDeclarations(self, file_handle):
		file_handle.write("signal ")
		file_handle.write(self.getOutputSignalName())
		file_handle.write(" : ")
		file_handle.write(self.vhdl_decl.getTypeDeclarations(self.getDataWidth()))
		file_handle.write(';\n')

class InstanceContainer:
	
	def __init__(self):
		self.msg = Messages()
		self.llvm_parser = LlvmParser()
		self.container = []
		self.assignmentMap = {}
		self.instanceMap = {}

	def resolveAssignment(self, assignment):
		if assignment in self.assignmentMap:
			return self.resolveAssignment(self.assignmentMap[assignment])
		return assignment

	def _resolveSource(self, operand):
		x = self.getAssignment(str(operand))
		return self.resolveAssignment(x.destination)

	def getSource(self, operand):
		x = self.resolveAssignment(operand)
		return x[1:] if x[0] == "%" else x

	def _addInstruction(self, destination : str, instruction : Instruction):
		instance = Instance(self)
		try:
			last_instance = self.container[-1]
			last_instance.next = instance
			instance.prev = last_instance
		except IndexError:
			pass
		instance.setInstruction(instruction)
		self.instanceMap[destination] = instance
		self.container.append(instance)

	def getAssignment(self, instruction : str):
		return self.llvm_parser.getAssignment(instruction)

	def _addCallInstruction(self, instruction):
		x = self.llvm_parser.getCallAssignment(instruction)
		self.msg.note(str(instruction))

	def _addAssignmentInstruction(self, instruction):
		x = self.getAssignment(str(instruction))
		self.assignmentMap[x.destination] = x.source

	def _addReturnInstruction(self, instruction):
		return_instruction = self.llvm_parser.getReturnInstruction(instruction)
		self.return_value = self.instanceMap[return_instruction.value].getOutputSignalName()

	def addInstruction(self, instruction, statistics):
		if instruction.opcode in ["add"]:
			statistics.increment(instruction.opcode)
			x = self.llvm_parser.getEqualAssignment(str(instruction))
			a = self.llvm_parser.getInstruction(x.source)
			self._addInstruction(x.destination, a)
		elif instruction.opcode == "call":
			x = self.llvm_parser.getEqualAssignment(str(instruction))
			self._addCallInstruction(x.source) 
		elif instruction.opcode in ["store", "load"]:
			self._addAssignmentInstruction(str(instruction))
		elif instruction.opcode == "ret":
			self._addReturnInstruction(str(instruction))
		elif instruction.opcode == "alloca":
			pass
		else:
			self.msg.error("Unknown instruction: " + str(instruction.opcode) + " (" + str(instruction) + ")")

	def writeInstances(self, file_handle):
		for i in self.container:
			i.writeInstance(file_handle)
		file_handle.write("return_value <= " + str(self.return_value) + ";\n")

	def writeDeclarations(self, file_handle):
		for i in self.container:
			i.writeDeclarations(file_handle)
			