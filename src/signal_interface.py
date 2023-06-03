
from abc import ABC, abstractmethod
from typing import Optional, Tuple


class SignalInterface(ABC):
    
    @abstractmethod
    def get_record_item(self) -> Optional[Tuple[str, str]]:
        pass

    @abstractmethod
    def get_signal_declaration(self) -> str:
        pass

    @abstractmethod
    def get_data_width(self) -> str:
        pass