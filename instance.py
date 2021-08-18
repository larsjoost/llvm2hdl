

class Instance:
	
	def __init__(self, instruction):
		self.library = "work"
		self.instruction = instruction
		self.next = None
		self.prev = None

	def getDataWidth(self):
		return self.instruction.type

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

	def print(self):
		instance_name = self.getInstanceName()
		print(instance_name, ": entity", self.library + "." + self.instruction.name, "is ", end="")
		input_ports = ""
		for index, operand in enumerate(self.instruction.operands):
			input_ports += ", " + chr(ord('a') + index) + " => " + str(operand)
		print("port map (clk => clk, sreset => sreset",
			", tag_in => " + self.getPreviousTagName(),
			input_ports,
			", tag_out => " + self.getNextTagName(),
			", q => " + self.instruction.name,
			");")	

class InstanceContainer:
	
	def __init__(self):
		self.container = []

	def add(self, instance):
		try:
			last_instance = self.container[-1]
			last_instance.next = instance
			instance.prev = last_instance
		except IndexError:
			pass
		self.container.append(instance)

	def addInstruction(self, instruction):
		if instruction.name in ["add"]:
			self.add(Instance(instruction))	

	def print(self):
		for i in self.container:
			i.print()