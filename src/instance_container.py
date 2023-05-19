from typing import List

from instance import DeclarationData, Instance
from instance_container_data import InstanceContainerData
from instance_container_interface import InstanceContainerInterface
from source_info import SourceInfo, SourceInfoMap
from llvm_instruction import LlvmInstructionContainer, LlvmInstructionInstance
from ports import Port

class InstanceContainer(InstanceContainerInterface):

    _container: List[Instance]
    _source_info_map: SourceInfoMap
    
    def __init__(self, instructions: LlvmInstructionContainer, input_ports: List[Port]):
        self._container = []
        self._source_info_map = SourceInfoMap()
        for i in instructions.instructions:
            self._add_instruction(instruction=i)
        for j in input_ports:
            source_info: SourceInfo = j.get_source_info()
            if source_info.destination is not None:
                self._source_info_map.add(type=source_info.destination, source_info=source_info)

    def _add_instruction(self, instruction : LlvmInstructionInstance) -> None:
        if not instruction.is_valid():
            return
        instance = Instance(instruction)
        destination = instruction.get_destination()
        if destination is not None:
            self._source_info_map.add(type=destination, source_info=instance.get_source_info())
        self._container.append(instance)
        
    def get_instances(self, source_info: SourceInfoMap) -> InstanceContainerData:
        instances = [i.get_instance_data(source_info=source_info) for i in self._container]
        return InstanceContainerData(instances=instances)

    def get_declarations(self) -> List[DeclarationData]:
        return [i.get_declaration_data() for i in self._container]
            