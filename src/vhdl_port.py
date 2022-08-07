from abc import ABC, abstractmethod
from dataclasses import dataclass
from signal import signal
from typing import Generator, List, Optional, Tuple, Union
from unittest import result

from ports import OutputPort, Port
from instance_data import InstanceData
from vhdl_declarations import VhdlSignal
from llvm_parser import InstructionArgument, LlvmOutputPort
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
    def get_signal_name(self, instance: InstanceData) -> str:
        return self.role.get_signal_name(instance=instance, name=self.name)
    def get_port_map(self, instance: InstanceData) -> str:
        signal_name = self.get_signal_name(instance=instance)
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

class VhdlMemoryPort:

    _memory_ports: List[VhdlPort] = [
    VhdlOutputPort(name="araddr", role=VhdlMasterPort(), data_width=VhdlMemoryAddressWidth()),
    VhdlOutputPort(name="arid", role=VhdlMasterPort(), data_width=VhdlMemoryIdWidth()),
    VhdlOutputPort(name="arvalid", role=VhdlMasterPort()),
    VhdlInputPort(name="arready", role=VhdlSlavePort()),
    VhdlOutputPort(name="rready", role=VhdlMasterPort()),
    VhdlInputPort(name="rvalid", role=VhdlSlavePort()),
    VhdlInputPort(name="rdata", role=VhdlSlavePort(), data_width=VhdlMemoryDataWidth()),
    VhdlInputPort(name="rid", role=VhdlSlavePort(), data_width=VhdlMemoryIdWidth()),
    VhdlOutputPort(name="awaddr", role=VhdlMasterPort(), data_width=VhdlMemoryAddressWidth()),
    VhdlOutputPort(name="awid", role=VhdlMasterPort(), data_width=VhdlMemoryIdWidth()),
    VhdlOutputPort(name="awvalid", role=VhdlMasterPort()),
    VhdlInputPort(name="awready", role=VhdlSlavePort()),
    VhdlOutputPort(name="wdata", role=VhdlMasterPort(), data_width=VhdlMemoryDataWidth()),
    VhdlInputPort(name="wid", role=VhdlMasterPort(), data_width=VhdlMemoryIdWidth()),
    VhdlOutputPort(name="wvalid", role=VhdlMasterPort()),
    VhdlInputPort(name="wready", role=VhdlSlavePort()),
    VhdlOutputPort(name="bready", role=VhdlMasterPort()),
    VhdlInputPort(name="bvalid", role=VhdlSlavePort()),
    VhdlInputPort(name="bid", role=VhdlSlavePort(), data_width=VhdlMemoryIdWidth())
    ]

    def __init__(self):
        self._msg = Messages()

    def _get_port_map(self, prefix: str, name: Union[str, List[str]], memory_port_name: str, unknown_port_name: bool) -> str:
        self._msg.function_start(f"prefix={prefix}, name={name}, memory_port_name={memory_port_name}, unknown_port_name={unknown_port_name}")
        if not isinstance(name, list):
            name = [name]
        port_map = " & ".join([f"{i}_{memory_port_name}" for i in name])
        if not unknown_port_name:
            port_map = f"{prefix}_{memory_port_name} => {port_map}"
        self._msg.function_end(port_map)
        return port_map

    def get_port_map(self, name: Union[str, List[str]], master: bool, unknown_port_name: bool = False) -> List[str]:
        self._msg.function_start(f"name={name}, master={master}, unknown_port_name={unknown_port_name}")
        prefix = "m" if master else "s"
        result = [self._get_port_map(prefix, name, i.name, unknown_port_name) for i in self._memory_ports]
        self._msg.function_end(result)
        return result

    def get_port_signals(self, name: str, scale_range: Optional[str] = None) -> List[str]:
        self._msg.function_start(f"name={name}")
        result = [f"{name}_{i.name} : {i.get_signal_type(scale_range=scale_range)}" for i in self._memory_ports]
        self._msg.function_end(result)
        return result

    def _get_signal_assignment(self, port: VhdlPort, signal_name: str, assignment_names: List[str]) -> str:
        self._msg.function_start(f"port={port}, signal_name={signal_name}, assignment_names={assignment_names}")
        assignment_separator = ", " if port.is_master() else " & "
        assignment = assignment_separator.join([f"{i}_{port.name}" for i in assignment_names])
        port_name = f"{signal_name}_{port.name}"
        result = f"({assignment}) <= {port_name}" if port.is_master() else f"{port_name} <= {assignment}"
        self._msg.function_end(result)
        return result

    def get_signal_assignments(self, signal_name: str, assignment_names: List[str]) -> List[str]:
        self._msg.function_start(f"signal_name={signal_name}, assignment_names={assignment_names}")
        result = [f"{self._get_signal_assignment(port=i, signal_name=signal_name, assignment_names=assignment_names)}" for i in self._memory_ports]
        self._msg.function_end(result)
        return result

    def get_ports(self, port: Port) -> List[str]:
        name = port.get_name()
        return [f"{name}_{i.get_port_definition()}" for i in self._memory_ports]
        
class VhdlPortGenerator:

    _standard_ports = [
    VhdlInputPort(name="clk"),
    VhdlInputPort(name="sreset"),
    VhdlInputPort(name="s_tvalid", role=VhdlSlavePort(connection="m_tvalid")),
    VhdlOutputPort(name="s_tready", role=VhdlSlavePort(connection="m_tready")),
    VhdlOutputPort(name="m_tvalid", role=VhdlMasterPort()),
    VhdlInputPort(name="m_tready", role=VhdlMasterPort())
    ]

    
    def __init__(self) -> None:
        self._msg = Messages()

    def get_tag_elements(self, ports: List[Port], signals: List[VhdlSignal]) -> Generator[Tuple[str, str], None, None]:
        yield ("tag", ": std_ulogic_vector(0 to s_tag'length - 1);")
        for port in ports:
            if port.is_input():
                yield (port.get_name(), f": std_ulogic_vector(0 to {port.get_name()}" + "'length - 1);")
        for signal in signals:
            yield signal.get_record_item()

    def get_tag_item_names(self, ports: List[Port], signals : List[VhdlSignal]) -> List[str]:
        self._msg.function_start(f"ports={ports}, signals={signals}")
        record_items = [name for name, _ in self.get_tag_elements(ports=ports, signals=signals)]
        self._msg.function_end(record_items)
        return record_items

    def _get_input_port_signal_name(self, input_port: InstructionArgument) -> str:
        self._msg.function_start(f"input_port={str(input_port)}")
        signal_name = input_port.get_name()
        array_index = input_port.get_array_index()
        if array_index is not None:
            signal_name += f"_{array_index}"
        if input_port.is_integer():
            signal_name = f"integer_{signal_name}"
        self._msg.function_end(signal_name)
        return signal_name

    def get_ports(self, port: Port) -> List[str]:
        name = port.get_name()
        direction = "in" if port.is_input() else "out"
        result = [f"{name} : {direction} std_ulogic_vector"]
        if port.is_pointer():
            result.extend(VhdlMemoryPort().get_ports(port=port))
        return result

    def get_port_map(self, input_port: InstructionArgument, memory_interface_name: Optional[str] = None) -> List[str]:
        self._msg.function_start(f"input_port={input_port}", True)
        input_port_signal_name = self._get_input_port_signal_name(input_port)
        input_port_map = input_port_signal_name
        if input_port.port_name is not None:
            input_port_map = f"{input_port.port_name} => {input_port_map}"
        result = [input_port_map]
        if input_port.is_pointer() and memory_interface_name is not None:
            result.extend(VhdlMemoryPort().get_port_map(name=memory_interface_name, master=True, unknown_port_name=True))
        self._msg.function_end(result, True)
        return result
 
    def get_output_port_map(self, output_port: LlvmOutputPort) -> List[str]:
        self._msg.function_start(f"output_port={output_port}", True)
        port_map = "m_tdata_i"
        if output_port.port_name is not None:
            port_map = f"{output_port.get_name()} => {port_map}"
        result = [port_map]
        self._msg.function_end(result, True)
        return result

    def get_port_signal(self, input_port: InstructionArgument) -> str:
        self._msg.function_start(f"input_port={input_port}")
        signal_name = self._get_input_port_signal_name(input_port)
        data_width = input_port.get_data_width()
        vector_range = f"(0 to {data_width} - 1)"
        result = f"signal {signal_name} : std_ulogic_vector{vector_range};"
        self._msg.function_end(result)
        return result

    def _is_tag_element(self, input_port: InstructionArgument, ports: List[Port], signals: List[VhdlSignal]) -> bool:
        self._msg.function_start(f"input_port={input_port}")
        name = input_port.signal_name.get_name()
        tag_item_names = self.get_tag_item_names(ports=ports, signals=signals)
        result = name in tag_item_names
        self._msg.function_end(result)
        return result

    def _get_input_port_name(self, input_port: InstructionArgument, ports: List[Port], signals: List[VhdlSignal]) -> str:
        self._msg.function_start(f"input_port={input_port}")
        signal_name = input_port.get_value()
        if self._is_tag_element(input_port=input_port, ports=ports, signals=signals):
            signal_name = f"tag_i.{signal_name}"
        self._msg.function_end(signal_name)
        return signal_name
    
    def _get_port_map_arguments(self, input_port: InstructionArgument, ports: List[Port], signals: List[VhdlSignal]) -> List[str]:
        self._msg.function_start(f"input_port={input_port}")
        signal_name = self._get_input_port_name(input_port=input_port, ports=ports, signals=signals)
        data_width = input_port.get_data_width()
        arguments = [signal_name, data_width]
        array_index = input_port.get_array_index()
        if array_index is not None:
            arguments.append(array_index)
        self._msg.function_end(arguments)
        return arguments

    def get_port_signal_assignment(self, input_port: InstructionArgument, ports: List[Port], signals: List[VhdlSignal]) -> str:
        self._msg.function_start(f"input_port={input_port}")
        signal_name = self._get_input_port_signal_name(input_port)
        arguments = self._get_port_map_arguments(input_port=input_port, ports=ports, signals=signals)
        argument_list = ", ".join(arguments)
        result = f"{signal_name} <= get({argument_list});"
        self._msg.function_end(result)
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
