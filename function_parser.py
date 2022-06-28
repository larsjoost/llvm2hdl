from typing import List, Optional, Union
from llvmlite.binding import ValueRef, TypeRef

from file_writer import FileWriter
from instance_container import InstanceContainer
from llvm_declarations import LlvmDeclarations
from llvm_parser import LlvmParser
from messages import Messages
from vhdl_declarations import VhdlDeclarations

class FunctionParser:

    def __init__(self):
        self._msg = Messages()
        self._instance_container = InstanceContainer()
        
    def _get_port(self, name: str, direction: str, data_width: Union[int, str], 
    default_value: Optional[str] = None) -> str:
        port_type: str = VhdlDeclarations(data_width).get_type_declarations()
        if default_value is not None:
            port_type += " := " + default_value
        return name + " : " + direction + " " + port_type

    def _get_data_width(self, t):
        data_type = t.split(' ')[0]
        return LlvmDeclarations(data_type).get_data_width()

    def _add_argument(self, name: str, type: TypeRef, ports: List[str]):
        data_width = self._get_data_width(str(type))
        ports.append(self._get_port(name, "in", data_width))

    def _write_declarations(self, type: str, instances: List[str], file_handle: FileWriter):
        file_handle.write_header(type + " (")
        file_handle.write_header(";\n".join(instances))
        file_handle.write_header(");")

    def _write_generics(self, file_handle: FileWriter, generics: List[str]):
        self._write_declarations("generic", generics, file_handle)
        
    def _write_ports(self, file_handle: FileWriter, ports: List[str]):
        self._write_declarations("port", ports, file_handle)

    def _get_entity_name(self, name: str) -> str:
        return LlvmParser().get_entity_name(name)

    def parse(self, function: ValueRef, file_handle: FileWriter, statistics):								
        self._msg.function_start("parse(function=" + str(function) + ")")
        if function.is_declaration:
            return
        return_data_width = self._get_data_width(str(function.type))
        return_name = "return_value"
        tag_input_name = "tag_in"
        tag_output_name = "tag_out"
        generics = [
            "tag_width : positive := 1"]
        ports = []
        for argument in function.arguments:
            self._add_argument(argument.name, argument.type, ports)
        ports.extend([
            self._get_port(return_name, "out", return_data_width),
            "clk : in std_ulogic",
            "sreset : in std_ulogic",
            self._get_port(tag_input_name, "in", "tag_width", "(others => '0')"),
            self._get_port(tag_output_name, "out", "tag_width")])
        for block in function.blocks:
            for i in block.instructions:
                self._instance_container.add_instruction(i, statistics)
        file_handle.write_header("library ieee;")
        file_handle.write_header("use ieee.std_logic_1164.all;")
        file_handle.write_header("library llvm;")
        file_handle.write_header("use llvm.llvm_pkg.conv_std_ulogic_vector;")
        file_handle.write_header("library work;")
        entity_name = self._get_entity_name(function.name)
        file_handle.write_header("entity " + entity_name + " is")
        self._write_generics(file_handle, generics)
        self._write_ports(file_handle, ports)
        file_handle.write_header("begin")
        file_handle.write_header("end entity " + entity_name + ";")
        file_handle.write_header("architecture rtl of " + entity_name + " is")
        self._instance_container.write_declarations(file_handle)
        self._instance_container.write_instances(file_handle)
        file_handle.write_trailer("end architecture rtl;")
        self._msg.function_end("parse")