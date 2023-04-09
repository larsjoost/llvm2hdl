from function_definition import FunctionDefinition
from instance_container import InstanceContainer
from llvm_function import LlvmFunction

class FunctionParser:
    
    def parse(self, function: LlvmFunction) -> FunctionDefinition:								
        input_ports = function.get_input_ports()
        instance_container = InstanceContainer(instructions=function.instructions, 
                                               input_ports=input_ports)
        return FunctionDefinition(function=function, instance_container=instance_container)
