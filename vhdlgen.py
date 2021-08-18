

from instance import InstanceContainer


class FunctionParser:

	def __init__(self):
		self.instance_container = InstanceContainer()

	def getPort(self, name, direction, data_width, default_value=None):
		port_type = "std_ulogic" if data_width == 1 else "std_ulogic_vector(0 to " + str(data_width) + " - 1)"
		if default_value is not None:
			port_type += " := " + default_value
		return name + " : " + direction + " " + port_type

	def getDataWidth(self, t):
		data_types = {'i32': 32}
		data_type = t.split(' ')[0]
		return data_types[data_type]

	def addArgument(self, name, type):
		data_width = self.getDataWidth(str(type))
		self.ports.append(self.getPort(name, "in", data_width))

	def printInstances(self):
		library = "work"
		if len(self.library) > 0:
			library = self.library
	
	def printDeclarations(self, type, instances):
		print(type, " (")
		delimiter = ""
		for i in instances:
			print(delimiter, i, end="")
			delimiter = ";\n"
		print(");")

	def printGenerics(self):
		self.printDeclarations("generic", self.generics)
		
	def printPorts(self):
		self.printDeclarations("port", self.ports)


	def parse(self, f):								
		self.name = f.name
		self.return_data_width = self.getDataWidth(str(f.type))
		self.return_name = "return_value"
		tagInputName = "tag_in"
		tagOutputName = "tag_out"
		self.ports = [
			self.getPort("clk", "in", 1),
			self.getPort("sreset", "in", 1),
			self.getPort(tagInputName, "in", "tag_width", "(others => '0')"),
			self.getPort(tagOutputName, "out", "tag_width"),
			self.getPort(self.return_name, "out", self.return_data_width)]
		self.generics = [
			"tag_width : positive := 1"]
		print(f'Function attributes: {list(f.attributes)}')
		for a in f.arguments:
			self.addArgument(a.name, a.type)
		for b in f.blocks:
			for i in b.instructions:
				self.instance_container.addInstruction(i)
		print("entity " + f.name + " is")
		self.printGenerics()
		self.printPorts()
		print("end entity " + f.name + ";")
		print("architecture rtl of " + f.name + " is)")
		print("begin")
		self.instance_container.print()
		print("end architecture " + f.name + ";")

class VhdlGen:

	def parse(self, m):
		for f in m.functions:
			x = FunctionParser()
			x.parse(f)
		for g in m.global_variables:
			print(f'Global: {g.name}/`{g.type}`')
			assert g.is_global
			print(f'Attributes: {list(g.attributes)}')
			print(g)

	def print_tree(self, m):
		for f in m.functions:
			print(f'Function: {f.name}/`{f.type}`')
			assert f.module is m
			assert f.function is None
			assert f.block is None
			assert f.is_function and not (f.is_block or f.is_instruction)
			print(f'Function attributes: {list(f.attributes)}')
			for a in f.arguments:
				print(f'Argument: {a.name}/`{a.type}`')
				print(f'Argument attributes: {list(a.attributes)}')
			for b in f.blocks:
				print(f'Block: {b.name}/`{b.type}`\n{b}\nEnd of Block')
				assert b.module is m
				assert b.function is f
				assert b.block is None
				assert b.is_block and not (b.is_function or b.is_instruction)
				for i in b.instructions:
					print(f'Instruction: {i.name}/`{i.opcode}`/`{i.type}`: `{i}`')
					print(f'Attributes: {list(i.attributes)}')
					assert i.module is m
					assert i.function is f
					assert i.block is b
					assert i.is_instruction and not (i.is_function or i.is_block)
					for o in i.operands:
						print(f'Operand: {o.name}/{o.type}')

		for g in m.global_variables:
			print(f'Global: {g.name}/`{g.type}`')
			assert g.is_global
			print(f'Attributes: {list(g.attributes)}')
			print(g)

	
