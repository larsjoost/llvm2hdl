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
        
    def _get_port(self, name: str, direction: str, data_width: Union[int, str], 
    default_value: Optional[str] = None) -> str:
        port_type: str = VhdlDeclarations(data_width).get_type_declarations()
        if default_value is not None:
            port_type += " := " + default_value
        return name + " : " + direction + " " + port_type

    def _get_data_width(self, type: str) -> LlvmDeclarations:
        data_type = type.split(' ')[0]
        return LlvmDeclarations(data_type).get_data_width()

    def _add_argument(self, name: str, type: TypeRef, ports: List[str]):
        data_width = self._get_data_width(str(type))
        ports.append(self._get_port(name, "in", data_width))

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
        instance_container = InstanceContainer()
        for block in function.blocks:
            for i in block.instructions:
                instance_container.add_instruction(i, statistics)
        entity_name = self._get_entity_name(function.name)
        instances = instance_container.get_instances()
        declarations = instance_container.get_declarations()
        file_handle.write_function(entity_name=entity_name, instances=instances, declarations=declarations,
        ports=ports, generics=generics)
        self._msg.function_end("parse")