from dataclasses import dataclass

@dataclass
class VhdlInstanceName:
    name: str
    library: str = "work"
    def get_entity_name(self) -> str:
        return self.name.replace("@", "").strip("_").replace("__", "_")
