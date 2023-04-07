

from dataclasses import dataclass

@dataclass
class VhdlSignalName:
    instance_name: str
    signal_name: str

    def get_signal_name(self) -> str:
        return f"{self.instance_name}_{self.signal_name}_i"
