
from dataclasses import dataclass
from typing import List
from function_definition import FunctionDefinition

from ports import PortContainer
from vhdl_instance_container_data import VhdlInstanceContainerData, VhdlInstanceContainerDataFactory
from vhdl_instance_data import VhdlDeclarationDataContainer, VhdlDeclarationDataFactory
from vhdl_instance_name import VhdlInstanceName
from function_logger import log_entry_and_exit

@dataclass
class VhdlFunctionDefinition:
    entity_name: str
    instances: VhdlInstanceContainerData
    declarations: VhdlDeclarationDataContainer
    ports: PortContainer
    def get_memory_port_names(self) -> List[str]:
        return self.ports.get_memory_port_names()

class VhdlFunctionDefinitionFactory:

    def get(self, function_definition: FunctionDefinition) -> VhdlFunctionDefinition:
        entity_name = VhdlInstanceName(name=function_definition.entity_name).get_entity_name()
        instances = VhdlInstanceContainerDataFactory().get(instance_container=function_definition.instances)
        declarations = VhdlDeclarationDataContainer(declarations=[VhdlDeclarationDataFactory().get(i) for i in function_definition.declarations])
        return VhdlFunctionDefinition(entity_name=entity_name, instances=instances, 
        declarations=declarations, ports=function_definition.ports)
