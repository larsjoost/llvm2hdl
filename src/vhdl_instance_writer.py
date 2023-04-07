
from language_generator import LanguageGenerator
from vhdl_comment_generator import VhdlCommentGenerator
from ports import PortContainer
from vhdl_function_container import VhdlFunctionContainer
from vhdl_function_definition import VhdlFunctionDefinition
from vhdl_instance_container_data import VhdlInstanceContainerData

class VhdlInstanceWriter:

    def _write_input_tag_assignment(self, ports: PortContainer, generator: LanguageGenerator) -> None:
        generator.write_body("tag_in_i.tag <= s_tag;")
        for port in ports.ports:
            if port.is_input():
                name = port.get_name()
                generator.write_body(f"tag_in_i.{name} <= {name};")

    def _write_output_tag_assignment(self, instances: VhdlInstanceContainerData, generator: LanguageGenerator) -> None:
        return_driver = instances.get_return_instruction_driver()
        comment = VhdlCommentGenerator().get_comment() 
        generator.write_body(f"""
{comment}
m_tvalid <= {return_driver}_m_tvalid_i;
{return_driver}_m_tready_i <= m_tready;
m_tdata <= conv_std_ulogic_vector(tag_out_i.{return_driver}, m_tdata'length);
m_tag <= tag_out_i.tag;
        """)

    def write_instances(self, function: VhdlFunctionDefinition, generator: LanguageGenerator, container: VhdlFunctionContainer) -> None:
        self._write_input_tag_assignment(ports=function.ports, generator=generator)
        function.generate_code(generator=generator, container=container)
        self._write_output_tag_assignment(instances=function.instances, generator=generator)
