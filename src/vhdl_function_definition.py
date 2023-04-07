
from dataclasses import dataclass
from typing import List
from function_definition import FunctionDefinition
from language_generator import LanguageGenerator
from llvm_function import LlvmFunction
from llvm_globals_container import GlobalsContainer

from ports import PortContainer
from vhdl_function_container import VhdlFunctionContainer
from vhdl_instance_container_data import VhdlInstanceContainerData, VhdlInstanceContainerDataFactory
from vhdl_instance_data import VhdlDeclarationDataContainer, VhdlDeclarationDataFactory
from vhdl_instance_name import VhdlInstanceName

@dataclass
class VhdlFunctionDefinition:
    entity_name: str
    instances: VhdlInstanceContainerData
    declarations: VhdlDeclarationDataContainer
    ports: PortContainer
    function: LlvmFunction
    def get_memory_port_names(self) -> List[str]:
        return self.ports.get_memory_port_names()
    def generate_code(self, generator: LanguageGenerator, container: VhdlFunctionContainer):
        self.function.generate_code(generator=generator, container=container)

class VhdlFunctionDefinitionFactory:

    def get(self, function_definition: FunctionDefinition, globals: GlobalsContainer) -> VhdlFunctionDefinition:
        entity_name = VhdlInstanceName(name=function_definition.entity_name).get_entity_name()
        instances = VhdlInstanceContainerDataFactory().get(instance_container=function_definition.instances, globals=globals)
        declarations = VhdlDeclarationDataContainer(declarations=[VhdlDeclarationDataFactory().get(i) for i in function_definition.declarations])
        return VhdlFunctionDefinition(entity_name=entity_name, instances=instances, 
        declarations=declarations, ports=function_definition.ports, function=function_definition.function)
