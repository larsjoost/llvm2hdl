

from dataclasses import dataclass
from typing import Any, List, Optional

from instance_data import DeclarationData, InstanceData
from instruction_interface import MemoryInterface
from llvm_instruction import LlvmInstruction
from llvm_port import LlvmOutputPort
from llvm_type_declaration import TypeDeclaration
from vhdl_instance_name import VhdlInstanceName
from vhdl_instruction_argument import VhdlInstructionArgument, VhdlInstructionArgumentFactory

from function_logger import log_entry_and_exit

@dataclass
class VhdlInstanceData:
    instance_name: str
    entity_name: str
    library: str
    output_port: Optional[LlvmOutputPort]
    tag_name: str
    generic_map: Optional[List[str]]
    input_ports: List[VhdlInstructionArgument]
    previous_instance_name: Optional[str]
    memory_interface: Optional[MemoryInterface]
    instruction: LlvmInstruction
    def _get_signal_name(self, instance_name: str, signal_name: str) -> str:
        return f"{instance_name}_{signal_name}_i"
    def get_previous_instance_signal_name(self, signal_name: str) -> Optional[str]:
        if self.previous_instance_name is None:
            return None
        return self._get_signal_name(instance_name=self.previous_instance_name, signal_name=signal_name)
    def get_own_instance_signal_name(self, signal_name) -> str:
        return self._get_signal_name(instance_name=self.instance_name, signal_name=signal_name)
    def is_memory(self) -> bool:
        return self.instruction.is_memory()
    def map_memory_interface(self) -> bool:
        return self.instruction.map_function_arguments()
    def get_memory_port_name(self, port: VhdlInstructionArgument) -> Optional[str]:
        if not port.is_pointer():
            return None
        if not self.map_memory_interface():
            return None
        memory_interface_name = self.instance_name
        return f"{memory_interface_name}_{port.get_name()}"
    def _remove_none_elements(self, elements: List[Any]) -> List[Any]:
        return [i for i in elements if i is not None]
    def get_memory_instance_names(self) -> List[str]:
        if self.memory_interface is not None and self.memory_interface.is_master():
            return [self.instance_name]
        result = [self.get_memory_port_name(port=i) for i in self.input_ports]
        return self._remove_none_elements(elements=result)
    def is_work_library(self) -> bool:
        return self.library == "work"
    def get_output_port_type(self) -> str:
        assert self.output_port is not None, f"Instance {self.instance_name} output port is not defined"
        return self.output_port.get_type_declarations()
    def get_source_line(self) -> str:
        return self.instruction.get_source_line()

@dataclass
class VhdlDeclarationData:
    instance_name: str
    declaration_name: str
    data_type: TypeDeclaration

    def is_void(self) -> bool:
        return self.data_type.is_void()

class VhdlDeclarationDataFactory:

    def get(self, declaration_data: DeclarationData) -> VhdlDeclarationData:
        instance_name = VhdlInstanceName(name=declaration_data.instance_name).get_entity_name()
        declaration_name = VhdlInstanceName(name=declaration_data.declaration_name).get_entity_name()
        return VhdlDeclarationData(instance_name=instance_name, declaration_name=declaration_name,
        data_type=declaration_data.data_type)

@dataclass
class VhdlDeclarationDataContainer:
    declarations: List[VhdlDeclarationData]

class VhdlInstanceDataFactory:
    
    def get(self, instance_data: InstanceData) -> VhdlInstanceData:
        instance_name = VhdlInstanceName(name=instance_data.instance_name).get_entity_name()
        entity_name = VhdlInstanceName(name=instance_data.entity_name, library=instance_data.library).get_entity_name()
        tag_name = VhdlInstanceName(name=instance_data.tag_name).get_entity_name()
        previous_instance_name = None
        if instance_data.previous_instance_name is not None:
            previous_instance_name = VhdlInstanceName(name=instance_data.previous_instance_name).get_entity_name()
        input_ports = [VhdlInstructionArgumentFactory().get(instruction_argument=i) for i in instance_data.input_ports]
        return VhdlInstanceData(instance_name=instance_name,
        entity_name=entity_name, 
        library=instance_data.library,
        output_port=instance_data.output_port,
        tag_name=tag_name,
        generic_map=instance_data.generic_map,
        input_ports=input_ports,
        previous_instance_name=previous_instance_name,
        memory_interface=instance_data.memory_interface,
        instruction=instance_data.instruction
        )