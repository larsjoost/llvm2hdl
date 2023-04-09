from dataclasses import dataclass
from typing import List, Optional
from instruction_argument import InstructionArgumentContainer

from source_info import SourceInfo, SourceInfoMap
from instance_data import DeclarationData, InstanceData
from llvm_type_declaration import TypeDeclaration
from llvm_type import LlvmVariableName
from llvm_parser import InstructionArgument
from llvm_instruction import LlvmInstructionInterface
from instance_interface import InstanceInterface

@dataclass
class Instance(InstanceInterface):

    instruction: LlvmInstructionInterface

    def get_instance_name(self) -> str:
        instance_name = self.instruction.get_instance_name()
        assert instance_name is not None
        return instance_name

    def get_tag_name(self) -> str:
        return f"{self.get_instance_name()}_tag_out_i"

    def get_output_signal_name(self) -> LlvmVariableName:
        return LlvmVariableName(self.get_instance_name())	

    def get_instance_tag_name(self, instance: Optional[InstanceInterface], default: str) -> str:
        return default if instance is None else instance.get_tag_name()	

    def get_data_type(self) -> Optional[TypeDeclaration]:
        return self.instruction.get_data_type()

    def _resolve_operand(self, operand: InstructionArgument, source_info: SourceInfoMap) -> InstructionArgument:
        source: Optional[SourceInfo] = source_info.get_source(search_source=operand.signal_name)
        if source is not None:
            operand.signal_name = source.output_signal_name
        return operand

    def get_source_info(self) -> SourceInfo:
        data_type = self.get_data_type()
        assert data_type is not None
        return SourceInfo(destination=self.instruction.get_destination(),
        output_signal_name=self.get_output_signal_name(),
        data_type=data_type)

    def _get_input_ports(self, operands: Optional[InstructionArgumentContainer], source_info: SourceInfoMap) -> List[InstructionArgument]:
        input_ports: List[InstructionArgument] = []
        if operands is not None:
            input_ports.extend(self._resolve_operand(operand=operand, source_info=source_info) for operand in operands.arguments)
        return input_ports

    def get_instance_data(self, source_info: SourceInfoMap) -> InstanceData:
        instance_name = self.get_instance_name()
        entity_name = self.instruction.get_instance_name()
        output_port = self.instruction.get_output_port()
        tag_name = self.get_tag_name()
        input_ports = self._get_input_ports(operands=self.instruction.get_operands(), source_info=source_info)
        memory_interface = self.instruction.get_memory_interface()
        library = self.instruction.get_library()
        assert entity_name is not None
        assert library is not None
        return InstanceData(instance_name=instance_name, entity_name=entity_name, library=library, 
        output_port=output_port, tag_name=tag_name, input_ports=input_ports, 
        memory_interface=memory_interface, instruction=self.instruction)

    def get_declaration_data(self) -> DeclarationData:
        data_type = self.instruction.get_data_type()
        assert data_type is not None
        return DeclarationData(instance_name=self.get_instance_name(), declaration_name=self.get_tag_name(), data_type=data_type)
