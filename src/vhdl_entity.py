
from typing import List
from ports import PortContainer
from vhdl_port_generator import VhdlPortGenerator
from vhdl_instance_name import VhdlInstanceName

class VhdlEntity:
    
    def _get_ports(self, ports: PortContainer) -> List[str]:
        entity_ports = ports.get_ports(generator=VhdlPortGenerator())
        standard_ports = VhdlPortGenerator().get_standard_ports_definition()
        tag_ports = ["s_tag : IN std_ulogic_vector", "m_tag : out std_ulogic_vector"] 
        return entity_ports + standard_ports + tag_ports

    def get_port_names(self, ports: PortContainer) -> List[str]:
        port_definition = self._get_ports(ports=ports)
        return [i.split()[0] for i in port_definition]

    def _get_port_definition(self, ports: PortContainer) -> str:
        all_ports = ";\n".join(self._get_ports(ports=ports))
        return f"""
port (
{all_ports}
);
        """

    def get_entity_name(self, name: str) -> str:
        return VhdlInstanceName(name=name).get_entity_name()

    def get_entity(self, entity_name: str, ports: PortContainer) -> str:
        return f"""
entity {entity_name} is
{self._get_port_definition(ports=ports)}
end entity {entity_name};
        """
        
