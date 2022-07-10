from typing import List, Optional, Union

from file_writer import FileWriter
from global_variables import GlobalVariables
from instance_container import InstanceContainer
from llvm_declarations import LlvmDeclaration, LlvmName, VectorDeclaration, BooleanDeclaration
from llvm_parser import LlvmFunction, LlvmParser
from messages import Messages
from ports import OutputPort, InputPort, Port

class FunctionParser:

    def __init__(self):
        self._msg = Messages()
        
    def _get_data_type(self, type: str) -> LlvmDeclaration:
        data_type = type.split(' ')[0]
        return LlvmDeclaration(data_type)

    def _get_entity_name(self, name: str) -> str:
        return LlvmParser().get_entity_name(name)

    def parse(self, function: LlvmFunction, file_handle: FileWriter, statistics):								
        self._msg.function_start("function=" + str(function))
        output_port = [OutputPort(name="m_tdata", data_type=function.return_type)]
        ports: List[Port] = [InputPort(name=i.signal_name, data_type=i.data_type) for i in function.arguments]
        instance_container = InstanceContainer()
        for instruction in function.instructions:
            instance_container.add_instruction(instruction, statistics)
        entity_name = self._get_entity_name(function.name)
        instances = instance_container.get_instances()
        declarations = instance_container.get_declarations()
        file_handle.write_function(entity_name=entity_name, instances=instances, declarations=declarations,
        ports=ports + output_port)
        self._msg.function_end()