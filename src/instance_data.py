from typing import List, Optional

from dataclasses import dataclass
from llvm_instruction import LlvmInstruction
from llvm_parser import InstructionArgument, MemoryInterface, LlvmOutputPort
from llvm_type_declaration import TypeDeclaration
from function_logger import log_entry_and_exit

@dataclass
class InstanceData:
    instance_name: str
    entity_name: str
    library: str
    output_port: Optional[LlvmOutputPort]
    tag_name: str
    generic_map: Optional[List[str]]
    input_ports: List[InstructionArgument]
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
    def get_memory_port_name(self, port: InstructionArgument) -> Optional[str]:
        memory_interface_name = self.instance_name if self.map_memory_interface() else None
        return f"{memory_interface_name}_{port.get_name()}" if memory_interface_name is not None else None
    def get_memory_instance_names(self) -> List[str]:
        if self.memory_interface is not None and self.memory_interface.is_master():
            return [self.instance_name]
        result = [self.get_memory_port_name(port=i) for i in self.input_ports]
        return [i for i in result if i is not None]
    def is_work_library(self) -> bool:
        return self.library == "work"
    def get_output_port_type(self) -> str:
        assert self.output_port is not None, f"Instance {self.instance_name} output port is not defined"
        return self.output_port.get_type_declarations()

@dataclass
class DeclarationData:
    instance_name: str
    declaration_name: str
    data_type: TypeDeclaration

    def is_void(self) -> bool:
        return self.data_type.is_void()

