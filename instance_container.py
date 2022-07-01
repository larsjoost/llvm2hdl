from typing import Dict, List
from llvmlite.binding import ValueRef

from instance import DeclarationData, Instance
from instance_container_data import InstanceContainerData
from instance_container_interface import InstanceContainerInterface
from instance_statistics import InstanceStatistics
from llvm_parser import EqualAssignment, LlvmParser, Instruction, ReturnInstruction, Alloca
from messages import Messages

class InstanceContainer(InstanceContainerInterface):
    
    _container: List[Instance] = []
    _alloca_map: Dict[str, Alloca] = {}
    _return_value: ReturnInstruction
    
    def __init__(self):
        self._msg = Messages()
        self._llvm_parser = LlvmParser()
        self._assignment_map = {}
        self._instance_map = {}

    def resolve_assignment(self, assignment: str) -> str:
        self._msg.function_start("resolve_assignment(assignment=" + assignment + ")")
        if assignment in self._assignment_map:
            return self.resolve_assignment(self._assignment_map[assignment])
        self._msg.function_end("resolve_assignment = " + str(assignment))
        return assignment

    def _resolve_source(self, operand):
        x = self.get_assignment(str(operand))
        return self.resolve_assignment(x.destination)

    def get_source(self, operand):
        x = self.resolve_assignment(operand)
        return x[1:] if x[0] == "%" else x

    def _add_instruction(self, destination : str, instruction : Instruction):
        self._msg.function_start("_add_instruction(destination=" + destination + ", instruction=" + str(instruction) + ")")
        instance = Instance(self)
        try:
            last_instance = self._container[-1]
            last_instance._next = instance
            instance._prev = last_instance
        except IndexError:
            pass
        instance.set_instruction(instruction)
        self._instance_map[destination] = instance
        self._assignment_map[destination] = instance.get_output_signal_name()
        self._container.append(instance)
        self._msg.function_end("_add_instruction")

    def get_assignment(self, instruction : str):
        return self._llvm_parser.get_assignment(instruction)

    def _add_call_instruction(self, instruction: str):
        self._msg.function_start("_add_call_instruction(instruction=" + instruction + ")")
        assignment: EqualAssignment = self._llvm_parser.get_equal_assignment(str(instruction))
        instruction: Instruction = self._llvm_parser.get_call_assignment(assignment.source)
        self._add_instruction(assignment.destination, instruction)
        self._msg.function_end("_add_call_instruction")

    def _add_alloca(self, instruction: str):
        assignment: EqualAssignment = self._llvm_parser.get_equal_assignment(str(instruction))
        alloca: Alloca = self._llvm_parser.get_alloca_assignment(assignment.source)
        self._alloca_map[assignment.destination] = alloca

    def _add_assignment_instruction(self, instruction: str):
        x = self.get_assignment(instruction)
        self._assignment_map[x.destination] = x.source

    def _get_return_instruction_driver(self, return_instruction: ReturnInstruction) -> str:
        return self._instance_map[return_instruction.value].get_instance_name()
        
    def _add_return_instruction(self, instruction: str) -> ReturnInstruction:
        self._msg.function_start("add_return_instruction(instruction=" + str(instruction) + ")")
        result: ReturnInstruction = self._llvm_parser.get_return_instruction(instruction)
        self._msg.function_end("_add_return_instruction = " + str(result))
        return result

    def _internal_llvm_call(self, instruction: str) -> bool:
        return "@llvm" in instruction

    def add_instruction(self, instruction: ValueRef, statistics: InstanceStatistics):
        self._msg.function_start("add_instruction(instruction=" + str(instruction) + ")")
        if instruction.opcode == "call":
            if not self._internal_llvm_call(str(instruction)):
                self._add_call_instruction(str(instruction))  
        elif instruction.opcode in ["store", "load", "bitcast", "getelementptr"]:
            self._add_assignment_instruction(str(instruction))
        elif instruction.opcode == "ret":
            self._return_value = self._add_return_instruction(str(instruction))
        elif instruction.opcode == "alloca":
            self._add_alloca(str(instruction))
        else:
            statistics.increment(instruction.opcode)
            assignment: EqualAssignment = self._llvm_parser.get_equal_assignment(str(instruction))
            instruction: Instruction = self._llvm_parser.get_instruction(assignment.source)
            self._add_instruction(assignment.destination, instruction)
        self._msg.function_end("add_instruction")

    def get_instances(self) -> InstanceContainerData:
        self._msg.function_start("get_instances()")
        instances = [i.get_instance_data() for i in self._container]
        return_instruction_driver = self._get_return_instruction_driver(return_instruction=self._return_value)
        result = InstanceContainerData(instances=instances, return_instruction_driver=return_instruction_driver,
        return_data_type=self._return_value.data_type)
        self._msg.function_end("get_instances = " + str(result))
        return result

    def get_declarations(self) -> List[DeclarationData]:
        return [i.get_declaration_data() for i in self._container]
            