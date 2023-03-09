from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator, List, Optional, Tuple, Union

from ports import Port, PortContainer, PortGenerator
from vhdl_declarations import VhdlSignal
from llvm_parser import LlvmOutputPort
from messages import Messages
from vhdl_instance_data import VhdlInstanceData
from vhdl_instruction_argument import VhdlInstructionArgument

@dataclass
class VhdlPortRole(ABC):
    connection: Optional[str] = None 
    def is_master(self) -> bool:
        return False
    def is_slave(self) -> bool:
        return False
    def get_signal_name(self, instance: VhdlInstanceData, name: str) -> str:
        return name

@dataclass
class VhdlMasterPort(VhdlPortRole):
    def is_master(self) -> bool:
        return True
    def get_signal_name(self, instance: VhdlInstanceData, name: str) -> str:
        return instance.get_own_instance_signal_name(name)

@dataclass
class VhdlSlavePort(VhdlPortRole):
    def is_slave(self) -> bool:
        return True
    def get_signal_name(self, instance: VhdlInstanceData, name: str) -> str:
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
    def get_signal_name(self, instance: VhdlInstanceData) -> str:
        return self.role.get_signal_name(instance=instance, name=self.name)
    def get_port_map(self, instance: VhdlInstanceData) -> str:
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
    VhdlOutputPort(name="wdata", role=VhdlMasterPort(), data_width=VhdlMemoryDataWidth()),
    VhdlOutputPort(name="wid", role=VhdlMasterPort(), data_width=VhdlMemoryIdWidth()),
    VhdlOutputPort(name="wvalid", role=VhdlMasterPort()),
    VhdlInputPort(name="wready", role=VhdlSlavePort()),
    VhdlOutputPort(name="bready", role=VhdlMasterPort()),
    VhdlInputPort(name="bvalid", role=VhdlSlavePort()),
    VhdlInputPort(name="bid", role=VhdlSlavePort(), data_width=VhdlMemoryIdWidth())
    ]

    def __init__(self):
        self._msg = Messages()

    def _get_port_map(self, prefix: str, name: Union[str, List[str]], memory_port_name: str, unknown_port_name: bool) -> str:
        if not isinstance(name, list):
            name = [name]
        port_map = " & ".join([f"{i}_{memory_port_name}" for i in name])
        if not unknown_port_name:
            port_map = f"{prefix}_{memory_port_name} => {port_map}"
        return port_map

    def get_port_map(self, name: Union[str, List[str]], master: bool, unknown_port_name: bool = False) -> List[str]:
        prefix = "m" if master else "s"
        return [
            self._get_port_map(prefix, name, i.name, unknown_port_name)
            for i in self._memory_ports
        ]

    def get_port_signals(self, name: str, scale_range: Optional[str] = None) -> List[str]:
        return [
            f"{name}_{i.name} : {i.get_signal_type(scale_range=scale_range)}"
            for i in self._memory_ports
        ]

    def _get_signal_assignment(self, port: VhdlPort, signal_name: str, assignment_names: List[str]) -> str:
        assignment_separator = " & " if port.is_master() else ", "
        assignment = assignment_separator.join([f"{i}_{port.name}" for i in assignment_names])
        destination_assignment = f"({assignment})" if len(assignment_names) > 1 else assignment
        port_name = f"{signal_name}_{port.name}"
        return (
            f"{port_name} <= {assignment}"
            if port.is_master()
            else f"{destination_assignment} <= {port_name}"
        )

    def get_signal_assignments(self, signal_name: str, assignment_names: List[str]) -> List[str]:
        return [
            f"{self._get_signal_assignment(port=i, signal_name=signal_name, assignment_names=assignment_names)}"
            for i in self._memory_ports
        ]

    def get_ports(self, port: Port) -> List[str]:
        name = port.get_name()
        return [f"{name}_{i.get_port_definition()}" for i in self._memory_ports]
        
class VhdlPortGenerator(PortGenerator):

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

    def get_tag_elements(self, ports: PortContainer, signals: List[VhdlSignal]) -> Generator[Tuple[str, str], None, None]:
        yield ("tag", ": std_ulogic_vector(0 to s_tag'length - 1);")
        for port in ports.ports:
            if port.is_input():
                yield (
                    port.get_name(),
                    f": std_ulogic_vector(0 to {port.get_name()}'length - 1);",
                )
        for signal in signals:
            yield signal.get_record_item()

    def get_tag_item_names(self, ports: PortContainer, signals : List[VhdlSignal]) -> List[str]:
        return [
            name for name, _ in self.get_tag_elements(ports=ports, signals=signals)
        ]

    def _get_input_port_signal_name(self, input_port: VhdlInstructionArgument) -> str:
        return input_port.get_input_port_signal_name()

    def get_ports(self, port: Port) -> List[str]:
        name = port.get_name()
        direction = "in" if port.is_input() else "out"
        result = [f"{name} : {direction} std_ulogic_vector"]
        if port.is_pointer():
            result.extend(VhdlMemoryPort().get_ports(port=port))
        return result

    def get_port_map(self, input_port: VhdlInstructionArgument, memory_interface_name: Optional[str] = None) -> List[str]:
        input_port_signal_name = self._get_input_port_signal_name(input_port)
        input_port_map = input_port_signal_name
        if input_port.port_name is not None:
            input_port_map = f"{input_port.port_name} => {input_port_map}"
        result = [input_port_map]
        if input_port.is_pointer() and memory_interface_name is not None:
            result.extend(VhdlMemoryPort().get_port_map(name=memory_interface_name, master=True, unknown_port_name=input_port.unnamed))
        return result
 
    def get_output_port_map(self, output_port: Optional[LlvmOutputPort]) -> List[str]:
        if output_port is None:
            return []
        port_map = "m_tdata_i"
        if output_port.port_name is not None:
            port_map = f"{output_port.get_name()} => {port_map}"
        return [port_map]

    def get_port_signal(self, input_port: VhdlInstructionArgument) -> str:
        signal_name = self._get_input_port_signal_name(input_port=input_port)
        data_width = input_port.get_data_width()
        vector_range = f"(0 to {data_width} - 1)"
        return f"signal {signal_name} : std_ulogic_vector{vector_range};"

    def _is_tag_element(self, input_port: VhdlInstructionArgument, ports: PortContainer, signals: List[VhdlSignal]) -> bool:
        name = input_port.signal_name
        tag_item_names = self.get_tag_item_names(ports=ports, signals=signals)
        return name in tag_item_names

    def _get_input_port_name(self, input_port: VhdlInstructionArgument, ports: PortContainer, signals: List[VhdlSignal]) -> str:
        signal_name = input_port.get_value()
        if self._is_tag_element(input_port=input_port, ports=ports, signals=signals):
            signal_name = f"tag_i.{signal_name}"
        return signal_name
    
    def _get_port_map_arguments(self, input_port: VhdlInstructionArgument, 
                                ports: PortContainer, signals: List[VhdlSignal]) -> List[str]:
        signal_name = self._get_input_port_name(input_port=input_port, ports=ports, signals=signals)
        data_width = input_port.get_data_width()
        arguments = [signal_name, data_width]
        array_index = input_port.get_array_index()
        if array_index is not None:
            arguments.append(array_index)
        return arguments

    def get_port_signal_assignment(self, input_port: VhdlInstructionArgument, 
                                   ports: PortContainer, signals: List[VhdlSignal]) -> str:
        signal_name = self._get_input_port_signal_name(input_port)
        arguments = self._get_port_map_arguments(input_port=input_port, ports=ports, signals=signals)
        argument_list = ", ".join(arguments)
        return f"{signal_name} <= get({argument_list});"

    def get_standard_ports_map(self, instance: VhdlInstanceData) -> List[str]:
        return [i.get_port_map(instance=instance) for i in self._standard_ports]
    
    def _get_standard_port_signals(self, instance: VhdlInstanceData, port: VhdlPort) -> Optional[str]:
        if not port.is_master():
            return None
        signal_name = instance.get_own_instance_signal_name(port.name)
        return signal_name + port.get_port_type()

    def get_standard_ports_signals(self, instance: VhdlInstanceData) -> List[str]:
        result = [self._get_standard_port_signals(instance=instance, port=i) for i in self._standard_ports]
        return [i for i in result if i is not None]

    def get_standard_ports_definition(self) -> List[str]:
        return [i.get_port_definition() for i in self._standard_ports]

    def get_data_width(self, port: Port) -> str:
        return f"{port.get_name()}'length"
