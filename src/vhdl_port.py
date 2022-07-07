
from ports import Port


class VhdlPort:

    def __init__(self, port: Port):
        self.port = port

    def get_port(self) -> str:
        name = self.port.get_name()
        if self.port.is_pointer():
            data_width = self.port.get_data_width()
            memory_name = "memory_i" + str(data_width)
            return f"{name}_master : out {memory_name}_master_t; {name}_slave : in {memory_name}_slave_t"
        direction = "in" if self.port.is_input() else "out"
        return name + " : " + direction + " std_ulogic_vector"
