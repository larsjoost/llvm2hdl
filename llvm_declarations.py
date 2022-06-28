
from dataclasses import dataclass


@dataclass
class LlvmDeclarations:
    data_type: str

    def get_data_width(self) -> int:
        if self.data_type[0] == "i":
            return int(self.data_type[1:])
        data_types = {'float': 32}
        return data_types[self.data_type]
