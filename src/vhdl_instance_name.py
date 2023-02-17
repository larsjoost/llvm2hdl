from dataclasses import dataclass

from function_logger import log_entry_and_exit

@dataclass
class VhdlInstanceName:
    name: str
    library: str = "work"
    def get_entity_name(self) -> str:
        return self.name.replace("@", "").strip("_").replace("__", "_")
