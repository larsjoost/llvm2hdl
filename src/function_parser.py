from typing import List, Optional, Union
from llvmlite.binding import ValueRef, TypeRef

from file_writer import FileWriter
from global_variables import GlobalVariables
from instance_container import InstanceContainer
from llvm_declarations import LlvmDeclaration, LlvmName, VectorDeclaration, BooleanDeclaration
from llvm_parser import LlvmParser
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

    def parse(self, function: ValueRef, global_variables: GlobalVariables,
    file_handle: FileWriter, statistics):								
        self._msg.function_start("parse(function=" + str(function) + ")")
        if function.is_declaration:
            return
        return_data_type = self._get_data_type(str(function.type))
        output_port = [OutputPort(name="return_value", data_type=return_data_type)]
        ports: List[Port] = [InputPort(name=LlvmName(i.name), data_type=LlvmDeclaration(str(i.type))) for i in function.arguments]
        instance_container = InstanceContainer()
        for block in function.blocks:
            for i in block.instructions:
                instance_container.add_instruction(i, statistics)
        entity_name = self._get_entity_name(function.name)
        instances = instance_container.get_instances()
        declarations = instance_container.get_declarations()
        file_handle.write_function(entity_name=entity_name, instances=instances, declarations=declarations,
        ports=ports + output_port)
        self._msg.function_end("parse")