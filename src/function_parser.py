from typing import List

from file_writer import FunctionContents, FunctionGenerator
from function_definition import FunctionDefinition
from instance_container import InstanceContainer
from llvm_declarations import LlvmIntegerDeclaration
from llvm_type import LlvmName
from llvm_parser import LlvmFunction, CallInstructionParser
from llvm_constant import ConstantContainer
from messages import Messages
from ports import OutputPort, Port, PortContainer
from function_logger import log_entry_and_exit

class FunctionParser:

    def __init__(self):
        self._msg = Messages()
        
    def _get_data_type(self, type: str) -> LlvmIntegerDeclaration:
        data_type = type.split(' ')[0]
        return LlvmIntegerDeclaration(data_width=int(data_type))

    def _get_entity_name(self, name: str) -> str:
        return CallInstructionParser().get_entity_name(name)

    def parse(self, function: LlvmFunction, file_handle: FunctionGenerator) -> FunctionContents:								
        output_port: List[Port] = [OutputPort(name=LlvmName("m_tdata"), data_type=function.return_type)]
        input_ports: List[Port] = function.get_input_ports()
        instance_container = InstanceContainer(instructions=function.instructions, input_ports=input_ports)
        entity_name = self._get_entity_name(function.name)
        instances = instance_container.get_instances()
        declarations = instance_container.get_declarations()
        ports = PortContainer(input_ports + output_port)
        function_definition = FunctionDefinition(entity_name=entity_name, instances=instances, declarations=declarations,ports=ports)
        return file_handle.write_function(function=function_definition)
        