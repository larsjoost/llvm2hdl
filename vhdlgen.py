

from instance import InstanceContainer
from llvm_declarations import LlvmDeclarations
from vhdl_declarations import VhdlDeclarations

class FunctionParser:

	def __init__(self):
		self.instance_container = InstanceContainer()
		self.llvm_decl = LlvmDeclarations()
		self.vhdl_decl = VhdlDeclarations()

	def getPort(self, name, direction, data_width, default_value=None):
		port_type = self.vhdl_decl.getTypeDeclarations(data_width)
		if default_value is not None:
			port_type += " := " + default_value
		return name + " : " + direction + " " + port_type

	def getDataWidth(self, t):
		data_type = t.split(' ')[0]
		return self.llvm_decl.getDataWidth(data_type)

	def addArgument(self, name, type):
		data_width = self.getDataWidth(str(type))
		self.ports.append(self.getPort(name, "in", data_width))

	def printInstances(self):
		library = "work"
		if len(self.library) > 0:
			library = self.library
	
	def writeDeclarations(self, type, instances, file_handle):
		file_handle.write(type + " (\n")
		delimiter = ""
		for i in instances:
			file_handle.write(delimiter)
			file_handle.write(i)
			delimiter = ";\n"
		file_handle.write(");\n")

	def writeGenerics(self, file_handle):
		self.writeDeclarations("generic", self.generics, file_handle)
		
	def writePorts(self, file_handle):
		self.writeDeclarations("port", self.ports, file_handle)


	def parse(self, function, file_handle):								
		self.name = function.name
		self.return_data_width = self.getDataWidth(str(function.type))
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
		for a in function.arguments:
			self.addArgument(a.name, a.type)
		for b in function.blocks:
			for i in b.instructions:
				self.instance_container.addInstruction(i)
		file_handle.write("library ieee;\n")
		file_handle.write("use ieee.std_logic_1164.all;\n")
		file_handle.write("entity " + function.name + " is\n")
		self.writeGenerics(file_handle)
		self.writePorts(file_handle)
		file_handle.write("end entity " + function.name + ";\n")
		file_handle.write("architecture rtl of " + function.name + " is\n")
		self.instance_container.writeDeclarations(file_handle)
		file_handle.write("begin\n")
		self.instance_container.writeInstances(file_handle)
		file_handle.write("end architecture " + function.name + ";\n")

class VhdlGen:

	def parse(self, module, file_handle):
		for f in module.functions:
			x = FunctionParser()
			x.parse(f, file_handle)
		for g in module.global_variables:
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

	
