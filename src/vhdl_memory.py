
from dataclasses import dataclass

from vhdl_memory_port import VhdlMemoryPort

@dataclass
class VhdlMemory:
    size_bytes: str
    initialization: str
    name: str

    def get_memory_instance(self) -> str:
        vhdl_memory_port = VhdlMemoryPort()
        port_map = ",\n".join(vhdl_memory_port.get_port_map(name=self.name, master=False, unknown_port_name=False))
        return f"""
{self.name}_i: entity memory.ram
generic map (
size_bytes => {self.size_bytes},
initialization => {self.initialization}
)
port map (
clk => clk,
sreset => sreset,
{port_map}
);
        """

    def get_memory_signals(self) -> str:
        return "\n".join([f"signal {i};" for i in VhdlMemoryPort().get_port_signals(name=self.name)])
