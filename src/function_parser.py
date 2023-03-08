from function_definition import FunctionDefinition
from instance_container import InstanceContainer
from llvm_function import LlvmFunction

class FunctionParser:
    
    def parse(self, function: LlvmFunction) -> FunctionDefinition:								
        input_ports = function.get_input_ports()
        ports = function.get_ports()
        instance_container = InstanceContainer(instructions=function.instructions, 
                                               input_ports=input_ports)
        entity_name = function.name
        instances = instance_container.get_instances()
        declarations = instance_container.get_declarations()
        return FunctionDefinition(entity_name=entity_name, instances=instances, 
                                  declarations=declarations,ports=ports)
