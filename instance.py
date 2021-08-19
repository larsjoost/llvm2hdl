from dataclasses import dataclass
from messages import Messages
from vhdl_declarations import VhdlDeclarations
from llvm_declarations import LlvmDeclarations

class Instance:
	
	def __init__(self, parent):
		self.parent = parent
		self.library = "work"
		self.next = None
		self.prev = None
		self.llvm_decl = LlvmDeclarations()
		self.vhdl_decl = VhdlDeclarations()

	def setInstruction(self, instruction):
		self.instruction = instruction
		# %add = add nsw i32 %0, %1
		a = str(instruction).split("=")
		self.opcode = self.parent._removeEmptyElements(a)[0].strip()
		data_type = self.parent._removeEmptyElements(a[1].split(' '))[2]
		self.data_width = self.llvm_decl.getDataWidth(data_type) 

	def getDataWidth(self):
		return self.data_width

	def getInstanceIndex(self):
		if self.prev is None:
			return 1
		return self.prev.getInstanceIndex() + 1

	def getInstanceName(self):
		return "inst_" + self.instruction.name + "_" + str(self.getInstanceIndex())
		
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
		file_handle.write(instance_name + " : entity " + self.library + "." + self.instruction.name + " is ")
		input_ports = ""
		for index, operand in enumerate(self.instruction.operands):
			input_ports += ", " + chr(ord('a') + index) + " => " + str(self.parent.resolveOperand(operand))
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
		self.container = []
		self.assignmentMap = {}
		self.instanceMap = {}

	def resolveAssignment(self, assignment):
		if assignment in self.assignmentMap:
			return self.resolveAssignment(self.assignmentMap[assignment])
		return assignment

	def _resolveOperand(self, operand):
		x = self.getAssignment(str(operand))
		return self.resolveAssignment(x.destination)

	def resolveOperand(self, operand):
		x = self._resolveOperand(operand)
		return x[1:] if x[0] == "%" else x

	def _addInstruction(self, instruction):
		instance = Instance(self)
		try:
			last_instance = self.container[-1]
			last_instance.next = instance
			instance.prev = last_instance
		except IndexError:
			pass
		instance.setInstruction(instruction)
		self.instanceMap[instance.opcode] = instance
		self.container.append(instance)

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

	def _addAssignmentInstruction(self, instruction):
		x = self.getAssignment(str(instruction))
		self.assignmentMap[x.destination] = x.source

	def _addReturnInstruction(self, instruction):
		# ret i32 %add
		instance_reference = self._removeEmptyElements(str(instruction).split(' '))[2].strip()
		self.return_value = self.instanceMap[instance_reference].getOutputSignalName()

	def addInstruction(self, instruction, statistics):
		if instruction.opcode in ["add"]:
			statistics.increment(instruction.opcode)
			self._addInstruction(instruction)
		elif instruction.opcode in ["store", "load"]:
			self._addAssignmentInstruction(instruction)
		elif instruction.opcode == "ret":
			self._addReturnInstruction(instruction)
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
			