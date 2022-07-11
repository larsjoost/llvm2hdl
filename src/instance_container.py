from typing import Dict, List, Optional

from instance import DeclarationData, Instance
from instance_container_data import InstanceContainerData
from instance_container_interface import InstanceContainerInterface, SourceInfo
from instance_statistics import InstanceStatistics
from llvm_parser import LlvmInstruction, LlvmParser, Instruction, ReturnInstruction, AllocaInstruction
from messages import Messages
from llvm_declarations import LlvmName, LlvmType
from instance_interface import InstanceInterface
from ports import InputPort

class InstanceContainer(InstanceContainerInterface):

    _container: List[Instance] = []
    _source_info_map: Dict[LlvmName, SourceInfo] = {}
    _return_value: ReturnInstruction
    
    def __init__(self, instructions: List[LlvmInstruction], input_ports: List[InputPort]):
        self._msg = Messages()
        self._llvm_parser = LlvmParser()
        for i in instructions:
            self._add_instruction(instruction=i)
        for i in input_ports:
            source_info: SourceInfo = i.get_source_info()
            self._source_info_map[source_info.destination] = source_info

    def get_source(self, search_source: LlvmType) -> Optional[SourceInfo]:
        return self._source_info_map.get(search_source, None)

    def _add_instruction(self, instruction : LlvmInstruction) -> None:
        self._msg.function_start("instruction=" + str(instruction))
        if not instruction.is_command():
            return
        instance = Instance(self, instruction)
        try:
            last_instance = self._container[-1]
            last_instance._next = instance
            instance._prev = last_instance
        except IndexError:
            pass
        destination = instruction.get_destination()
        if destination is not None:
            self._source_info_map[destination] = instance.get_source_info()
        self._container.append(instance)
        self._msg.function_end()

    def get_instances(self) -> InstanceContainerData:
        self._msg.function_start()
        instances = [i.get_instance_data() for i in self._container]
        result = InstanceContainerData(instances=instances)
        self._msg.function_end(result)
        return result

    def get_declarations(self) -> List[DeclarationData]:
        return [i.get_declaration_data() for i in self._container]
            