
from ports import PortContainer
from vhdl_function import VhdlFunction
from vhdl_function_container import VhdlFunctionContainer
from vhdl_function_contents import VhdlFunctionContents
from vhdl_instance_generator import VhdlInstanceGenerator
from vhdl_module import VhdlModule

class VhdlInstanceWriter:

    def _write_input_tag_assignment(self, ports: PortContainer, function_contents: VhdlFunctionContents) -> None:
        function_contents.write_body("tag_in_i.tag <= s_tag;")
        for port in ports.ports:
            if port.is_input():
                name = port.get_name()
                function_contents.write_body(f"tag_in_i.{name} <= {name};")

    def write_instances(self, function: VhdlFunction, function_contents: VhdlFunctionContents, 
                        container: VhdlFunctionContainer, module: VhdlModule) -> None:
        self._write_input_tag_assignment(ports=function.get_ports(), function_contents=function_contents)
        instance_generator = VhdlInstanceGenerator()
        instance_generator.generate_code(function=function, function_contents=function_contents, container=container, module=module)
 