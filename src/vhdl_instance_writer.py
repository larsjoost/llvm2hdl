
from language_generator import LanguageGenerator
from ports import PortContainer
from vhdl_function_container import VhdlFunctionContainer
from vhdl_function_definition import VhdlFunctionDefinition

class VhdlInstanceWriter:

    def _write_input_tag_assignment(self, ports: PortContainer, generator: LanguageGenerator) -> None:
        generator.write_body("tag_in_i.tag <= s_tag;")
        for port in ports.ports:
            if port.is_input():
                name = port.get_name()
                generator.write_body(f"tag_in_i.{name} <= {name};")

    def write_instances(self, function: VhdlFunctionDefinition, generator: LanguageGenerator, container: VhdlFunctionContainer) -> None:
        self._write_input_tag_assignment(ports=function.ports, generator=generator)
        function.generate_code(generator=generator, container=container)
