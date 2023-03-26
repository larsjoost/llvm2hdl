
from vhdl_comment_generator import VhdlCommentGenerator
from ports import PortContainer
from vhdl_function_container import VhdlFunctionContainer
from vhdl_function_contents import VhdlFunctionContents
from vhdl_instance_container_data import VhdlInstanceContainerData
from vhdl_instantiation_groups import VhdlInstantiationGroupWriter

class VhdlInstanceWriter:

    def _write_input_tag_assignment(self, ports: PortContainer, function_contents: VhdlFunctionContents) -> None:
        function_contents.write_body("tag_in_i.tag <= s_tag;")
        for port in ports.ports:
            if port.is_input():
                name = port.get_name()
                function_contents.write_body(f"tag_in_i.{name} <= {name};")

    def _write_output_tag_assignment(self, instances: VhdlInstanceContainerData, function_contents: VhdlFunctionContents) -> None:
        return_driver = instances.get_return_instruction_driver()
        comment = VhdlCommentGenerator().get_comment() 
        function_contents.write_body(f"""
{comment}
m_tvalid <= {return_driver}_m_tvalid_i;
{return_driver}_m_tready_i <= m_tready;
m_tdata <= conv_std_ulogic_vector(tag_out_i.{return_driver}, m_tdata'length);
m_tag <= tag_out_i.tag;
        """)

    def write_instances(self, instances: VhdlInstanceContainerData, ports: PortContainer, function_contents: VhdlFunctionContents, container: VhdlFunctionContainer) -> None:
        self._write_input_tag_assignment(ports=ports, function_contents=function_contents)
        VhdlInstantiationGroupWriter().write_instances(instances=instances.instances, function_contents=function_contents, container=container)
        self._write_output_tag_assignment(instances=instances, function_contents=function_contents)
