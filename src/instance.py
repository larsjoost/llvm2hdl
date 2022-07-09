from typing import List

from assignment_resolution import AssignmentItem
from instance_container_interface import InstanceContainerInterface
from instance_data import DeclarationData, InstanceData
from llvm_declarations import LlvmDeclaration
from llvm_parser import InstructionArgument, LlvmParser, Instruction
from messages import Messages
from vhdl_declarations import VhdlDeclarations

class Instance:

    instruction: Instruction

    _parent: InstanceContainerInterface

    def __init__(self, parent: InstanceContainerInterface):
        self._msg = Messages()
        self._parent = parent
        self._next = None
        self._prev = None
        self._llvm_parser = LlvmParser()

    def set_instruction(self, instruction : Instruction):
        self.instruction = instruction

    def get_instance_index(self) -> int:
        if self._prev is None:
            return 1
        return self._prev.get_instance_index() + 1

    def get_instance_name(self) -> str:
        return self.instruction.opcode + "_" + str(self.get_instance_index())

    def get_tag_name(self) -> str:
        return self.get_instance_name() + "_tag_out_i"

    def get_output_signal_name(self) -> str:
        return self.get_instance_name()	

    def get_assignment(self,) -> AssignmentItem:
        return AssignmentItem(driver=self.get_output_signal_name(), 
        data_type=self.instruction.data_type)

    def get_instance_tag_name(self, instance, default: str) -> str:
        if instance is None:
            return default
        return instance.get_tag_name()	

    def get_previous_tag_name(self) -> str:
        return self.get_instance_tag_name(self._prev, "tag_in_i")	

    def _get_output_tag_name(self) -> str:
        if self._next is None:
            return "tag_out_i"
        return self.get_tag_name()	

    def _resolve_operand(self, operand: InstructionArgument) -> InstructionArgument:
        source: List[AssignmentItem] = self._parent.get_source(search_source=operand.signal_name)
        if len(source) > 0:
            operand.signal_name = source[-1].get_driver()
            operand.data_type = source[-1].data_type
            operand.data_type.data_type = source[0].data_type.data_type    
        return operand

    def _get_input_ports(self, operands: List[InstructionArgument], data_type: LlvmDeclaration) -> List[InstructionArgument]:
        self._msg.function_start("_get_input_ports(operands=" + str(operands) + ")")
        input_ports: List[InstructionArgument] = []
        for operand in operands:
            input_ports.append(self._resolve_operand(operand))
        self._msg.function_end("_get_input_ports = " + str(input_ports))
        return input_ports

    def get_instance_data(self) -> InstanceData:
        instance_name = self.get_instance_name()
        entity_name = self.instruction.opcode
        output_port = self.instruction.get_output_port()
        tag_name = self._get_output_tag_name()
        previous_instance_name = None if self._prev is None else self._prev.get_instance_name()
        input_ports = self._get_input_ports(operands=self.instruction.operands, 
        data_type=self.instruction.data_type)
        data = InstanceData(instance_name=instance_name, entity_name=entity_name, 
        library=self.instruction.library,
        output_port=output_port,tag_name=tag_name, input_ports=input_ports, 
        previous_instance_name=previous_instance_name)
        return data

    def get_declaration_data(self) -> DeclarationData:
        vhdl_decl = VhdlDeclarations(self.instruction.data_type)
        data = DeclarationData(instance_name=self.get_instance_name(), entity_name=self.get_tag_name(), 
        type=vhdl_decl)
        return data

