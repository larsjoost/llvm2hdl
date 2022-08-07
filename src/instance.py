from typing import List, Optional

from source_info import SourceInfo
from instance_container_interface import InstanceContainerInterface
from instance_data import DeclarationData, InstanceData
from llvm_declarations import LlvmDeclaration, LlvmName, TypeDeclaration
from llvm_parser import InstructionArgument, LlvmInstruction, LlvmParser
from messages import Messages
from instance_interface import InstanceInterface
from vhdl_declarations import VhdlDeclarations

class Instance(InstanceInterface):

    instruction: LlvmInstruction

    _parent: InstanceContainerInterface
    _prev: Optional[InstanceInterface]
    _next: Optional[InstanceInterface]


    def __init__(self, parent: InstanceContainerInterface, instruction : LlvmInstruction):
        self._msg = Messages()
        self._parent = parent
        self.instruction = instruction
        self._next = None
        self._prev = None
        self._llvm_parser = LlvmParser()

    def get_instance_index(self) -> int:
        return 1 if self._prev is None else self._prev.get_instance_index() + 1

    def get_instance_name(self) -> str:
        instance_name = self.instruction.get_instance_name()
        assert instance_name is not None
        return f"{instance_name}_{str(self.get_instance_index())}"

    def get_tag_name(self) -> str:
        return f"{self.get_instance_name()}_tag_out_i"

    def get_output_signal_name(self) -> LlvmName:
        return LlvmName(self.get_instance_name())	

    def get_instance_tag_name(self, instance: Optional[InstanceInterface], default: str) -> str:
        return default if instance is None else instance.get_tag_name()	

    def get_previous_tag_name(self) -> str:
        return self.get_instance_tag_name(self._prev, "tag_in_i")	

    def _get_output_tag_name(self) -> str:
        return "tag_out_i" if self._next is None else self.get_tag_name()	

    def get_data_type(self) -> Optional[TypeDeclaration]:
        return self.instruction.get_data_type()

    def _resolve_operand(self, operand: InstructionArgument) -> InstructionArgument:
        self._msg.function_start(f"operand={str(operand)}")
        source: Optional[SourceInfo] = self._parent.get_source(search_source=operand.signal_name)

        if source is not None:
            operand.signal_name = source.output_signal_name
        self._msg.function_end(operand)
        return operand

    def get_source_info(self) -> SourceInfo:
        data_type = self.get_data_type()
        assert data_type is not None
        return SourceInfo(destination=self.instruction.get_destination(),
        output_signal_name=self.get_output_signal_name(),
        data_type=data_type)

    def _get_input_ports(self, operands: Optional[List[InstructionArgument]]) -> List[InstructionArgument]:
        self._msg.function_start(f"operands={str(operands)}")
        input_ports: List[InstructionArgument] = []
        if operands is not None:
            input_ports.extend(self._resolve_operand(operand) for operand in operands)
        self._msg.function_end(input_ports)
        return input_ports

    def get_instance_data(self) -> InstanceData:
        instance_name = self.get_instance_name()
        entity_name = self.instruction.get_instance_name()
        output_port = self.instruction.get_output_port()
        tag_name = self._get_output_tag_name()
        previous_instance_name = None
        if self._prev is not None:
            previous_instance_name = self._prev.get_instance_name()
        input_ports = self._get_input_ports(operands=self.instruction.get_operands())
        generic_map = self.instruction.get_generic_map()
        memory_interface = self.instruction.get_memory_interface()
        library = self.instruction.get_library()
        assert entity_name is not None
        assert library is not None
        assert output_port is not None
        return InstanceData(instance_name=instance_name, entity_name=entity_name, library=library, output_port=output_port, tag_name=tag_name, generic_map=generic_map, input_ports=input_ports, previous_instance_name=previous_instance_name, memory_interface=memory_interface, instruction=self.instruction)

    def get_declaration_data(self) -> DeclarationData:
        data_type = self.instruction.get_data_type()
        assert data_type is not None
        vhdl_decl = VhdlDeclarations(data_type=data_type)
        return DeclarationData(instance_name=self.get_instance_name(), entity_name=self.get_tag_name(), type=vhdl_decl)

