from typing import List, Optional, Union
from messages import Messages
from ports import Port
from vhdl_port import VhdlInputPort, VhdlMasterPort, VhdlMemoryAddressWidth, VhdlMemoryDataWidth, VhdlMemoryIdWidth, VhdlOutputPort, VhdlPort, VhdlSlavePort
from vhdl_signal_assignment import VhdlSignalAssignment

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

    def _get_slave_signal_assignment(self, assignment: str, port_name: str, multiple_assignment_names: bool) -> str:
        destination_assignment = f"({assignment})" if multiple_assignment_names else assignment
        return f"{destination_assignment} <= {port_name}"

    def _get_master_signal_assignment(self, assignment: str, port_name: str) -> str:
        return f"{port_name} <= {assignment}"

    def _get_signal_assignment(self, port: VhdlPort, signal_name: str, assignment_names: List[VhdlSignalAssignment]) -> str:
        assignment_separator = " & " if port.is_master() else ", "
        memory_assignments = [i.get_name(port_name=port.name) for i in assignment_names]
        assignment = assignment_separator.join(memory_assignments)
        port_name = f"{signal_name}_{port.name}"
        if port.is_master():
            return self._get_master_signal_assignment(assignment=assignment, port_name=port_name)
        multiple_assignment_names = len(assignment_names) > 1
        return self._get_slave_signal_assignment(assignment=assignment, port_name=port_name, multiple_assignment_names=multiple_assignment_names)

    def get_signal_assignments(self, signal_name: str, assignment_names: List[VhdlSignalAssignment]) -> List[str]:
        return [
            f"{self._get_signal_assignment(port=i, signal_name=signal_name, assignment_names=assignment_names)}"
            for i in self._memory_ports
        ]

    def get_ports(self, port: Port) -> List[str]:
        name = port.get_name()
        return [f"{name}_{i.get_port_definition()}" for i in self._memory_ports]
        
