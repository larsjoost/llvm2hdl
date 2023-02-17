from typing import List

from function_definition import FunctionDefinition
from instance_container import InstanceContainer
from llvm_declarations import LlvmIntegerDeclaration
from llvm_type import LlvmVariableName
from llvm_function import LlvmFunction
from messages import Messages
from ports import OutputPort, Port, PortContainer
from function_logger import log_entry_and_exit

class FunctionParser:

    def __init__(self):
        self._msg = Messages()
        
    def _get_data_type(self, type: str) -> LlvmIntegerDeclaration:
        data_type = type.split(' ')[0]
        return LlvmIntegerDeclaration(data_width=int(data_type))

    def parse(self, function: LlvmFunction) -> FunctionDefinition:								
        output_port: List[Port] = [OutputPort(name=LlvmVariableName("m_tdata"), data_type=function.return_type)]
        input_ports: List[Port] = function.get_input_ports()
        instance_container = InstanceContainer(instructions=function.instructions, input_ports=input_ports)
        entity_name = function.name
        instances = instance_container.get_instances()
        declarations = instance_container.get_declarations()
        ports = PortContainer(input_ports + output_port)
        return FunctionDefinition(entity_name=entity_name, instances=instances, declarations=declarations,ports=ports)
        