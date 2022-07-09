from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator, List, Optional, Tuple

from ports import Port
from instance_data import InstanceData
from vhdl_declarations import VhdlSignal
from llvm_parser import InstructionArgument
from messages import Messages


@dataclass
class VhdlPortRole(ABC):
    connection: Optional[str] = None 
    def is_master(self) -> bool:
        return False
    def is_slave(self) -> bool:
        return False
    def get_signal_name(self, instance: InstanceData, name: str) -> str:
        return name

@dataclass
class VhdlMasterPort(VhdlPortRole):
    def is_master(self) -> bool:
        return True
    def get_signal_name(self, instance: InstanceData, name: str) -> str:
        return instance.get_own_instance_signal_name(name)

@dataclass
class VhdlSlavePort(VhdlPortRole):
    def is_slave(self) -> bool:
        return True
    def get_signal_name(self, instance: InstanceData, name: str) -> str:
        signal_name = instance.get_previous_instance_signal_name(name)
        if signal_name is None:
            return name
        if self.connection is not None:
            return signal_name.replace(name, self.connection)
        return signal_name

class VhdlGlobalPort(VhdlPortRole):
    pass

@dataclass
class VhdlPort(ABC):
    name: str
    data_type: str
    role: VhdlPortRole() = VhdlGlobalPort()
    def _get_port_type(self, direction: Optional[str] = None) -> str:
        return " : " + ("" if direction is None else direction + " ") + self.data_type
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
    def get_signal_name(self, instance: InstanceData) -> str:
        return self.role.get_signal_name(instance=instance, name=self.name)
    def get_port_map(self, instance: InstanceData) -> str:
        signal_name = self.get_signal_name(instance=instance)
        return f"{self.name} => {signal_name}"
        
class VhdlInputPort(VhdlPort):
    def get_port_definition(self) -> str:
        return self._get_port_definition("in")
    
class VhdlOutputPort(VhdlPort):
    def get_port_definition(self) -> str:
        return self._get_port_definition("out")

class VhdlPortGenerator:

    _memory_ports = [
    VhdlOutputPort(name="m_mem_addr", data_type="std_ulogic_vector"),
    VhdlOutputPort(name="m_mem_addr_id", data_type="std_ulogic_vector"),
    VhdlOutputPort(name="m_mem_addr_valid", data_type="std_ulogic"),
    VhdlOutputPort(name="m_mem_data", data_type="std_ulogic_vector"),
    VhdlOutputPort(name="m_mem_data_valid", data_type="std_ulogic"),
    VhdlOutputPort(name="m_mem_data_ready", data_type="std_ulogic"),
    VhdlOutputPort(name="m_mem_data_response_ready",  data_type="std_ulogic"),
    VhdlInputPort(name="s_mem_addr_ready", data_type="std_ulogic"),
    VhdlInputPort(name="s_mem_data_ready", data_type="std_ulogic"),
    VhdlInputPort(name="s_mem_data_valid", data_type="std_ulogic"),
    VhdlInputPort(name="s_mem_data", data_type="std_ulogic_vector"),
    VhdlInputPort(name="s_mem_data_id", data_type="std_ulogic_vector"),
    VhdlInputPort(name="s_mem_data_response_valid", data_type="std_ulogic"),
    VhdlInputPort(name="s_mem_data_response_id", data_type="std_ulogic_vector")
    ]

    _standard_ports = [
    VhdlInputPort(name="clk", data_type="std_ulogic"),
    VhdlInputPort(name="sreset", data_type="std_ulogic"),
    VhdlInputPort(name="s_tvalid", data_type="std_ulogic", role=VhdlSlavePort(connection="m_tvalid")),
    VhdlOutputPort(name="s_tready", data_type="std_ulogic", role=VhdlSlavePort(connection="m_tready")),
    VhdlOutputPort(name="m_tvalid", data_type="std_ulogic", role=VhdlMasterPort()),
    VhdlInputPort(name="m_tready", data_type="std_ulogic", role=VhdlMasterPort())
    ]

    
    def __init__(self) -> None:
        self._msg = Messages()

    def get_tag_elements(self, ports: List[Port], signals : List[VhdlSignal]) -> Generator[Tuple[str, str], None, None]:
        yield ("tag", ": std_ulogic_vector(0 to s_tag'length - 1);")
        for port in ports:
            if port.is_input():
                yield (port.get_name(), ": std_ulogic_vector(0 to " + port.get_name() + "'length - 1);")
        for signal in signals:
            yield signal.get_record_item()

    def get_tag_item_names(self, ports: List[Port], signals : List[VhdlSignal]) -> List[str]:
        self._msg.function_start("_get_tag_item_names()")
        record_items = [name for name, _ in self.get_tag_elements(ports=ports, signals=signals)]
        self._msg.function_end("_get_tag_item_names = " + str(record_items))
        return record_items

    def _get_input_port_signal_name(self, input_port: InstructionArgument) -> str:
        self._msg.function_start("_get_input_port_signal_name(input_port=" + str(input_port) + ")")
        signal_name = input_port.get_name()
        array_index = input_port.get_array_index()
        if array_index is not None:
            signal_name += "_" + array_index
        signal_name += "_i"
        if input_port.is_integer():
            signal_name = "integer_" + signal_name
        self._msg.function_end("_get_input_port_signal_name = " + signal_name)
        return signal_name

    def get_ports(self,port: Port) -> List[str]:
        name = port.get_name()
        direction = "in" if port.is_input() else "out"
        result = [name + " : " + direction + " std_ulogic_vector"]
        if port.is_pointer():
            result.extend([name + "_" + i.get_port_definition() for i in self._memory_ports])
        return result

    def get_port_map(self, input_port: InstructionArgument) -> str:
        self._msg.function_start("get_port_map(input_port=" + str(input_port) + ")")
        result = self._get_input_port_signal_name(input_port)
        if input_port.port_name is not None:
            result = input_port.port_name + " => " + result
        self._msg.function_end("get_port_map = " + str(result))
        return result

    def get_memory_port_map(self, input_port: InstructionArgument) -> List[str]:
        self._msg.function_start("get_port_map(input_port=" + str(input_port) + ")")
        name = input_port.get_name()
        result = [f"{i.name} => {name}_{i.name}" for i in self._memory_ports]
        self._msg.function_end("get_port_map = " + str(result))
        return result

    def get_port_signal(self, input_port: InstructionArgument) -> str:
        self._msg.function_start("_get_port_signal(input_port=" + str(input_port) + ")")
        signal_name = self._get_input_port_signal_name(input_port)
        data_width = input_port.get_data_width()
        vector_range = "(0 to " + data_width + " - 1)"
        result = "signal " + signal_name + " : std_ulogic_vector" + vector_range + ";"
        self._msg.function_end("_get_port_signal = " + result)
        return result

    def _is_tag_element(self, input_port: InstructionArgument, ports: List[Port], signals : List[VhdlSignal]) -> bool:
        self._msg.function_start("_is_tag_element(input_port=" + str(input_port) + ")")
        name = str(input_port.signal_name)
        tag_item_names = self.get_tag_item_names(ports=ports, signals=signals)
        result = name in tag_item_names
        self._msg.function_end("_is_tag_element = " + str(result))
        return result

    def _get_input_port_name(self, input_port: InstructionArgument, ports: List[Port], signals : List[VhdlSignal]) -> str:
        self._msg.function_start("_get_input_port_name(input_port=" + str(input_port) + ")")
        signal_name = input_port.get_value()
        if self._is_tag_element(input_port=input_port, ports=ports, signals=signals):
            signal_name = "tag_i." + signal_name
        self._msg.function_end("_get_input_port_name = " + signal_name)
        return signal_name
    
    def _get_port_map_arguments(self, input_port: InstructionArgument, ports: List[Port], signals : List[VhdlSignal]) -> List[str]:
        self._msg.function_start("_get_port_map_arguments(input_port=" + str(input_port) + ")")
        signal_name = self._get_input_port_name(input_port=input_port, ports=ports, signals=signals)
        data_width = input_port.get_data_width()
        arguments = [signal_name, data_width]
        array_index = input_port.get_array_index()
        if array_index is not None:
            arguments.append(array_index)
        self._msg.function_end("_get_port_map_arguments = " + str(arguments))
        return arguments

    def get_port_signal_assignment(self, input_port: InstructionArgument, ports: List[Port], signals : List[VhdlSignal]) -> str:
        self._msg.function_start("_get_port_signal_assignment(input_port=" + str(input_port) + ")")
        signal_name = self._get_input_port_signal_name(input_port)
        arguments = self._get_port_map_arguments(input_port=input_port, ports=ports, signals=signals)
        result = signal_name + " <= get(" + ", ".join(arguments) + ");"
        self._msg.function_end("_get_port_signal_assignment = " + str(result))
        return result

    def get_standard_ports_map(self, instance: InstanceData) -> List[str]:
        return [i.get_port_map(instance=instance) for i in self._standard_ports]
    
    def _get_standard_port_signals(self, instance: InstanceData, port: VhdlPort) -> Optional[str]:
        if not port.is_master():
            return None
        signal_name = instance.get_own_instance_signal_name(port.name)
        return signal_name + port.get_port_type()

    def get_standard_ports_signals(self, instance: InstanceData) -> List[str]:
        result = [self._get_standard_port_signals(instance=instance, port=i) for i in self._standard_ports]
        return [i for i in result if i is not None]

    def get_standard_ports_definition(self) -> List[str]:
        return [i.get_port_definition() for i in self._standard_ports]
