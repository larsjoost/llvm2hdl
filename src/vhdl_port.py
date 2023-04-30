from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from vhdl_signal_name import VhdlSignalName

@dataclass
class VhdlPortRole(ABC):
    connection: Optional[str] = None 
    def is_master(self) -> bool:
        return False
    def is_slave(self) -> bool:
        return False
    def get_signal_name(self, instance_name: str, previous_instance_name: Optional[str], name: str) -> str:
        return name

@dataclass
class VhdlMasterPort(VhdlPortRole):
    def is_master(self) -> bool:
        return True
    def get_signal_name(self, instance_name: str, previous_instance_name: Optional[str], name: str) -> str:
        return VhdlSignalName(instance_name=instance_name, signal_name=name).get_signal_name()

@dataclass
class VhdlSlavePort(VhdlPortRole):
    def is_slave(self) -> bool:
        return True
    def get_signal_name(self, instance_name: str, previous_instance_name: Optional[str], name: str) -> str:
        if previous_instance_name is None:
            return name
        signal_name = VhdlSignalName(instance_name=previous_instance_name, signal_name=name).get_signal_name()
        if self.connection is not None:
            return signal_name.replace(name, self.connection)
        return signal_name

class VhdlGlobalPort(VhdlPortRole):
    pass

class VhdlDataWidth(ABC):
    @abstractmethod
    def get_data_width(self) -> Optional[str]:
        pass
    def is_boolean(self) -> bool:
        return False

class VhdlMemoryAddressWidth(VhdlDataWidth):
    def get_data_width(self) -> str:
        return "c_mem_addr_width"

class VhdlMemoryDataWidth(VhdlDataWidth):
    def get_data_width(self) -> str:
        return "c_mem_data_width"

class VhdlMemoryIdWidth(VhdlDataWidth):
    def get_data_width(self) -> str:
        return "c_mem_id_width"

class VhdlBooleanWidth(VhdlDataWidth):
    def get_data_width(self) -> None:
        return None
    def is_boolean(self) -> bool:
        return True

@dataclass
class VhdlPortBase:
    name: str
    data_width: VhdlDataWidth = VhdlBooleanWidth()
    role: VhdlPortRole = VhdlGlobalPort()

class VhdlPort(ABC, VhdlPortBase):
    def _get_port_type(self, direction: Optional[str] = None) -> str:
        return " : " + ("" if direction is None else f"{direction} ") + self.get_type()
    def _get_port_definition(self, direction: str) -> str:
        return self.name + self._get_port_type(direction=direction)
    @abstractmethod
    def get_port_definition(self) -> str:
        pass
    def get_port_type(self) -> str:
        return self._get_port_type()
    def is_master(self) -> bool:
        return self.role.is_master()
    def is_slave(self) -> bool:
        return self.role.is_slave()
    def get_signal_name(self, instance_name: str, previous_instance_name: Optional[str]) -> str:
        return self.role.get_signal_name(instance_name=instance_name, previous_instance_name=previous_instance_name, name=self.name)
    def get_port_map(self, instance_name: str, previous_instance_name: Optional[str]) -> str:
        signal_name = self.get_signal_name(instance_name=instance_name, previous_instance_name=previous_instance_name)
        return f"{self.name} => {signal_name}"
    def get_type(self) -> str:
        return "std_ulogic" if self.data_width.is_boolean() else "std_ulogic_vector"
    def _get_signal_range(self, scale_range: Optional[str] = None) -> str:
        x = self.data_width.get_data_width()
        if scale_range is not None:
            x = scale_range if x is None else f"{x} * {scale_range}"
        return "" if x is None else f"(0 to {x} - 1)"
    def get_signal_type(self, scale_range: Optional[str] = None) -> str:
        data_type = self.get_type() if scale_range is None else "std_ulogic_vector"
        return f"{data_type}{self._get_signal_range(scale_range=scale_range)}"
    
class VhdlInputPort(VhdlPort):
    def get_port_definition(self) -> str:
        return self._get_port_definition("in")
    
class VhdlOutputPort(VhdlPort):
    def get_port_definition(self) -> str:
        return self._get_port_definition("out")
