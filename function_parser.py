from typing import List, Optional, Union
from llvmlite.binding import ValueRef, TypeRef

from file_writer import FileWriter
from instance import InstanceContainer
from llvm_declarations import LlvmDeclarations
from messages import Messages
from vhdl_declarations import VhdlDeclarations

class FunctionParser:

    def __init__(self):
        self._msg = Messages()
        self._instance_container = InstanceContainer()
        self.llvm_decl = LlvmDeclarations()
        self.vhdl_decl = VhdlDeclarations()

    def _get_port(self, name: str, direction: str, data_width: Union[int, str], 
    default_value: Optional[str] = None) -> str:
        port_type = self.vhdl_decl.get_type_declarations(data_width)
        if default_value is not None:
            port_type += " := " + default_value
        return name + " : " + direction + " " + port_type

    def _get_data_width(self, t):
        data_type = t.split(' ')[0]
        return self.llvm_decl.get_data_width(data_type)

    def _add_argument(self, name: str, type: TypeRef, ports: List[str]):
        data_width = self._get_data_width(str(type))
        ports.append(self._get_port(name, "in", data_width))

    def _write_declarations(self, type: str, instances: List[str], file_handle: FileWriter):
        file_handle.write(type + " (")
        file_handle.write(";\n".join(instances))
        file_handle.write(");")

    def _write_generics(self, file_handle: FileWriter, generics: List[str]):
        self._write_declarations("generic", generics, file_handle)
        
    def _write_ports(self, file_handle: FileWriter, ports: List[str]):
        self._write_declarations("port", ports, file_handle)

    def _get_entity_name(self, function) -> str:
        return "entity" + function.name

    def parse(self, function: ValueRef, file_handle: FileWriter, statistics):								
        self._msg.function_start("parse(function=" + str(function) + ")", True)
        if function.is_declaration:
            return
        self.return_data_width = self._get_data_width(str(function.type))
        self.return_name = "return_value"
        tag_input_name = "tag_in"
        tag_output_name = "tag_out"
        self.ports = [
            self._get_port("clk", "in", 1),
            self._get_port("sreset", "in", 1),
            self._get_port(tag_input_name, "in", "tag_width", "(others => '0')"),
            self._get_port(tag_output_name, "out", "tag_width"),
            self._get_port(self.return_name, "out", self.return_data_width)]
        self.generics = [
            "tag_width : positive := 1"]
        for argument in function.arguments:
            self._add_argument(argument.name, argument.type, self.ports)
        for block in function.blocks:
            for i in block.instructions:
                self._instance_container.add_instruction(i, statistics)
        file_handle.write("library ieee;")
        file_handle.write("use ieee.std_logic_1164.all;")
        file_handle.write("library llvm;")
        file_handle.write("entity " + self._get_entity_name(function) + " is")
        self._write_generics(file_handle, self.generics)
        self._write_ports(file_handle, self.ports)
        file_handle.write("begin")
        file_handle.write("end entity " + self._get_entity_name(function) + ";")
        file_handle.write("architecture rtl of " + self._get_entity_name(function) + " is")
        self._instance_container.write_declarations(file_handle)
        file_handle.write("begin")
        self._instance_container.write_instances(file_handle)
        file_handle.write("end architecture rtl;")
        self._msg.function_end("parse", True)