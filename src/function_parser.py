from typing import List

from function_definition import FunctionDefinition
from instance_container import InstanceContainer
from llvm_declarations import LlvmIntegerDeclaration
from llvm_function import LlvmFunction
from messages import Messages

class FunctionParser:

    def __init__(self):
        self._msg = Messages()
        
    def _get_data_type(self, type: str) -> LlvmIntegerDeclaration:
        data_type = type.split(' ')[0]
        return LlvmIntegerDeclaration(data_width=int(data_type))

    
    def parse(self, function: LlvmFunction) -> FunctionDefinition:								
        input_ports = function.get_input_ports()
        ports = function.get_ports()
        instance_container = InstanceContainer(instructions=function.instructions, input_ports=input_ports)
        entity_name = function.name
        instances = instance_container.get_instances()
        declarations = instance_container.get_declarations()
        return FunctionDefinition(entity_name=entity_name, instances=instances, declarations=declarations,ports=ports)
        