
from abc import ABC


class MemoryInterface(ABC):
    def is_master(self) -> bool:
        return False

class MemoryInterfaceMaster(MemoryInterface):
    def is_master(self) -> bool:
        return True

class MemoryInterfaceSlave(MemoryInterface):
    pass
