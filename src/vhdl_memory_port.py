from typing import List, Optional, Union
from messages import Messages
from ports import Port
from vhdl_port import VhdlInputPort, VhdlMasterPort, VhdlMemoryAddressWidth, VhdlMemoryDataWidth, VhdlMemoryIdWidth, VhdlOutputPort, VhdlPort, VhdlSlavePort


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

    def get_memory_signal_name(self, instance_name: str, signal_name: str) -> str:
        return f"{instance_name}_{signal_name}"

    def _get_signal_assignment(self, port: VhdlPort, signal_name: str, assignment_names: List[str]) -> str:
        assignment_separator = " & " if port.is_master() else ", "
        assignment = assignment_separator.join([self.get_memory_signal_name(instance_name=i, signal_name=port.name) for i in assignment_names])
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
        
