from typing import List, Optional

from source_info import SourceInfo
from instance_container_interface import InstanceContainerInterface
from instance_data import DeclarationData, InstanceData
from llvm_declarations import LlvmDeclaration, TypeDeclaration
from llvm_parser import InstructionArgument, LlvmInstruction, LlvmParser, Instruction
from messages import Messages
from instance_interface import InstanceInterface
from vhdl_declarations import VhdlDeclarations

class Instance(InstanceInterface):

    instruction: LlvmInstruction

    _parent: InstanceContainerInterface

    def __init__(self, parent: InstanceContainerInterface, instruction : LlvmInstruction):
        self._msg = Messages()
        self._parent = parent
        self.instruction = instruction
        self._next = None
        self._prev = None
        self._llvm_parser = LlvmParser()

    def get_instance_index(self) -> int:
        if self._prev is None:
            return 1
        return self._prev.get_instance_index() + 1

    def get_instance_name(self) -> str:
        return self.instruction.get_opcode() + "_" + str(self.get_instance_index())

    def get_tag_name(self) -> str:
        return self.get_instance_name() + "_tag_out_i"

    def get_output_signal_name(self) -> str:
        return self.get_instance_name()	

    def get_instance_tag_name(self, instance: Optional[InstanceInterface], default: str) -> str:
        if instance is None:
            return default
        return instance.get_tag_name()	

    def get_previous_tag_name(self) -> str:
        return self.get_instance_tag_name(self._prev, "tag_in_i")	

    def _get_output_tag_name(self) -> str:
        if self._next is None:
            return "tag_out_i"
        return self.get_tag_name()	

    def get_data_type(self) -> TypeDeclaration:
        return self.instruction.get_data_type()

    def _resolve_operand(self, operand: InstructionArgument) -> InstructionArgument:
        self._msg.function_start("operand=" + str(operand))
        source: Optional[SourceInfo] = self._parent.get_source(search_source=operand.signal_name)
        if source is not None:
            operand.signal_name = source.output_signal_name
            operand.data_type = source.data_type
        self._msg.function_end(operand)
        return operand

    def get_source_info(self) -> SourceInfo:
        return SourceInfo(destination=self.instruction.get_destination(),
        output_signal_name=self.get_output_signal_name(),
        data_type=self.get_data_type())

    def _get_input_ports(self, operands: List[InstructionArgument], data_type: LlvmDeclaration) -> List[InstructionArgument]:
        self._msg.function_start("operands=" + str(operands))
        input_ports: List[InstructionArgument] = []
        for operand in operands:
            input_ports.append(self._resolve_operand(operand))
        self._msg.function_end(input_ports)
        return input_ports

    def get_instance_data(self) -> InstanceData:
        instance_name = self.get_instance_name()
        entity_name = self.instruction.get_opcode()
        output_port = self.instruction.get_output_port()
        tag_name = self._get_output_tag_name()
        previous_instance_name = None if self._prev is None else self._prev.get_instance_name()
        input_ports = self._get_input_ports(operands=self.instruction.get_operands(),
        data_type=self.instruction.get_data_type())
        data = InstanceData(instance_name=instance_name, entity_name=entity_name,
        library=self.instruction.get_library(),
        output_port=output_port,tag_name=tag_name, input_ports=input_ports,
        previous_instance_name=previous_instance_name)
        return data

    def get_declaration_data(self) -> DeclarationData:
        vhdl_decl = VhdlDeclarations(self.instruction.get_data_type())
        data = DeclarationData(instance_name=self.get_instance_name(), entity_name=self.get_tag_name(), 
        type=vhdl_decl)
        return data

