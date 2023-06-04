
from dataclasses import dataclass
from typing import Optional


@dataclass
class VhdlSignalAssignment:
    instance_name: str
    signal_name: str

    def get_name(self, port_name: Optional[str] = None) -> str:
        name = f"{self.instance_name}_{self.signal_name}"
        if port_name is not None:
            name += f"_{port_name}"
        return name

    