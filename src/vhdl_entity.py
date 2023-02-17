

from dataclasses import dataclass
from ports import PortContainer
from vhdl_port import VhdlPortGenerator
from vhdl_instance_name import VhdlInstanceName

class VhdlEntity:
    
    def _get_ports(self, ports: PortContainer) -> str:
        x = ports.get_ports(generator=VhdlPortGenerator())
        standard_ports = VhdlPortGenerator().get_standard_ports_definition()
        tag_ports = ["s_tag : IN std_ulogic_vector", "m_tag : out std_ulogic_vector"] 
        all_ports = ";\n".join(x + standard_ports + tag_ports)
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
{self._get_ports(ports=ports)}
end entity {entity_name};
        """
        
