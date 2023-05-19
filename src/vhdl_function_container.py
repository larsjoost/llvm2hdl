


from dataclasses import dataclass, field
import inspect
from typing import List
from function_container_interface import FunctionContainerInterface
from signal_interface import SignalInterface
from vhdl_code_generator import VhdlCodeGenerator
from ports import PortContainer

from vhdl_file_writer_reference import VhdlFileWriterReference
from vhdl_file_writer_variable import VhdlFileWriterVariable

@dataclass
class Signals:
    comment : str
    signals : List[str]
    
class InstanceSignals:
    signals: List[Signals]
    def __init__(self) -> None:
        self.signals = []
    def get_signals(self) -> str:
        result = ""
        for i in self.signals:
            result += "\n" + i.comment + "\n"
            result += "\n".join(f"signal {instance_signal};" for instance_signal in i.signals)
        return result
    def add(self, signals: List[str], comment: str) -> None:
        self.signals.append(Signals(comment=comment, signals=signals))

@dataclass
class VhdlFunctionContainer(FunctionContainerInterface):
    signals : List[SignalInterface] = field(default_factory=list)
    instance_signals: InstanceSignals = field(default_factory=lambda : InstanceSignals())
    references: List[VhdlFileWriterReference] = field(default_factory=list)
    variables: List[VhdlFileWriterVariable] = field(default_factory=list)
    ports: PortContainer = field(default_factory=lambda : PortContainer())

    def add_instance_signals(self, signals: List[str]) -> None:
        comment = VhdlCodeGenerator().get_comment(current_frame=inspect.currentframe())
        self.instance_signals.add(signals=signals, comment=comment)
        
    def get_signals(self) -> List[SignalInterface]:
        return self.signals

    def get_ports(self) -> PortContainer:
        return self.ports
    
    def add_signal(self, signal: SignalInterface) -> None:
        self.signals.append(signal)
