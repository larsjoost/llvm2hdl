
from typing import Generator, List, Optional, Tuple
from llvm_port import LlvmOutputPort
from messages import Messages
from ports import Port, PortContainer, PortGenerator
from signal_interface import SignalInterface
from vhdl_instruction_argument import VhdlInstructionArgument
from vhdl_memory_port import VhdlMemoryPort
from vhdl_port import VhdlInputPort, VhdlMasterPort, VhdlOutputPort, VhdlPort, VhdlSlavePort


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

    def get_tag_elements(self, ports: PortContainer, signals: List[SignalInterface]) -> Generator[Tuple[str, str], None, None]:
        yield ("tag", ": std_ulogic_vector(0 to s_tag'length - 1);")
        for port in ports.ports:
            if port.is_input():
                yield (
                    f"var_{port.get_name()}",
                    f": std_ulogic_vector(0 to {port.get_name()}'length - 1);",
                )
        for signal in signals:
            record_item = signal.get_record_item()
            if record_item is not None:
                yield record_item

    def get_tag_item_names(self, ports: PortContainer, signals : List[SignalInterface]) -> List[str]:
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
        input_port_map = f"{input_port_signal_name}_i"
        if input_port.port_name is not None:
            input_port_map = f"{input_port.port_name} => {input_port_map}"
        result = [input_port_map]
        if input_port.is_pointer() and memory_interface_name is not None:
            result.extend(VhdlMemoryPort().get_port_map(name=memory_interface_name, master=True, unknown_port_name=input_port.unnamed))
        return result
 
    def get_output_port_map(self, output_port: Optional[LlvmOutputPort]) -> List[str]:
        if output_port is None:
            return []
        port_map = ["m_tdata => m_tdata_i"]
        if output_port.is_pointer():
            name = output_port.get_name()
            assert name is not None
            port_map.extend(VhdlMemoryPort().get_port_map(name=name, master=False))
        return port_map

    def get_port_signal(self, input_port: VhdlInstructionArgument) -> str:
        signal_name = self._get_input_port_signal_name(input_port=input_port)
        data_width = input_port.get_data_width()
        vector_range = f"(0 to {data_width} - 1)"
        return f"signal {signal_name}_i : std_ulogic_vector{vector_range};"

    def _get_input_port_name(self, input_port: VhdlInstructionArgument) -> str:
        if not input_port.is_variable():
            return input_port.get_value()
        variable_name = input_port.get_variable_name()
        return f"tag_i.{variable_name}"
    
    def _get_port_map_arguments(self, input_port: VhdlInstructionArgument) -> List[str]:
        signal_name = self._get_input_port_name(input_port=input_port)
        data_width = input_port.get_data_width()
        arguments = [signal_name, data_width]
        array_index = input_port.get_array_index()
        if array_index is not None:
            arguments.append(array_index)
        return arguments

    def get_port_signal_assignment(self, input_port: VhdlInstructionArgument) -> str:
        signal_name = self._get_input_port_signal_name(input_port)
        arguments = self._get_port_map_arguments(input_port=input_port)
        argument_list = ", ".join(arguments)
        return f"{signal_name}_i <= get({argument_list});"

    def get_standard_ports_map(self, instance_name: str, previous_instance_name: Optional[str]) -> List[str]:
        return [i.get_port_map(instance_name=instance_name, previous_instance_name=previous_instance_name) for i in self._standard_ports]
    
    def _get_signal_name(self, instance_name: str, signal_name: str) -> str:
        return f"{instance_name}_{signal_name}_i"
    
    def _get_standard_port_signals(self, instance_name: str, port: VhdlPort) -> Optional[str]:
        if not port.is_master():
            return None
        signal_name = self._get_signal_name(instance_name=instance_name, signal_name=port.name)
        return signal_name + port.get_port_type()

    def get_standard_ports_signals(self, instance_name: str) -> List[str]:
        result = [self._get_standard_port_signals(instance_name=instance_name, port=i) for i in self._standard_ports]
        return [i for i in result if i is not None]

    def get_standard_ports_definition(self) -> List[str]:
        return [i.get_port_definition() for i in self._standard_ports]

    def get_data_width(self, port: Port) -> str:
        return f"{port.get_name()}'length"
