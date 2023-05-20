
from typing import List
from vhdl_code_generator import VhdlCodeGenerator
from vhdl_function_contents import VhdlFunctionContents
from vhdl_memory import VhdlMemory
from vhdl_memory_port import VhdlMemoryPort

class VhdlMemoryGenerator:

    def _get_memory_arbiter_port_map(self, memory_master_name: str, memory_slave_name: str) -> str:
        vhdl_memory_port = VhdlMemoryPort()
        slave_memory_port_map = vhdl_memory_port.get_port_map(name=memory_slave_name, master=False)
        master_memory_port_map = vhdl_memory_port.get_port_map(name=memory_master_name, master=True)
        memory_port_map = slave_memory_port_map + master_memory_port_map
        return ", ".join(memory_port_map)

    def _get_memory_arbiter_instance(self, memory_interface_name: str, port_map: str) -> str:
        return f"""
{memory_interface_name}: entity memory.arbiter(rtl)
port map(
clk => clk, 
sreset => sreset,
{port_map}
);
        """        

    def _write_memory_instances(self, memory_name: str, number_of_memory_instances: int, 
                                memory_instance_names: List[str], function_contents: VhdlFunctionContents):
        memory_signal_name = "s"
        vhdl_memory_port = VhdlMemoryPort()
        block_name = f"arbiter_{memory_name}_b"
        signals = "\n".join([f"signal {i}; " for i in vhdl_memory_port.get_port_signals(name=memory_signal_name, scale_range="c_size")])
        signal_assigment_list = vhdl_memory_port.get_signal_assignments(signal_name=memory_signal_name, assignment_names=memory_instance_names)
        signal_assigments = "\n".join([f"{i};" for i in signal_assigment_list])
        memory_interface_name = f"memory_arbiter_{memory_name}"
        port_map = self._get_memory_arbiter_port_map(memory_master_name=memory_name, memory_slave_name=memory_signal_name)
        comment = VhdlCodeGenerator().get_comment() 
        memory_arbiter_instance = self._get_memory_arbiter_instance(memory_interface_name=memory_interface_name, port_map=port_map)
        function_contents.write_body(f"""
{comment}
{block_name}: block
constant c_size : positive := {number_of_memory_instances};
{signals}
begin

{signal_assigments}
        
{memory_arbiter_instance}

end block {block_name};

        """)

    def _get_memory_interface_signal_assignment(self, memory_master_name: str, memory_slave_name: str) -> str:
        vhdl_memory_port = VhdlMemoryPort()
        assignment_list = vhdl_memory_port.get_signal_assignments(signal_name=memory_master_name, assignment_names=[memory_slave_name])
        return "\n".join([f"{i};" for i in assignment_list])

    def _write_memory_interface_signal_assignment(self, memory_master_name: str, memory_slave_name: str, 
                                                  function_contents: VhdlFunctionContents) -> None:
        assignments = self._get_memory_interface_signal_assignment(memory_master_name=memory_master_name, memory_slave_name=memory_slave_name)
        function_contents.write_body(assignments)
        
    def _write_memory_arbiter(self, memory_instance_names: List[str], memory_name: str, 
                              function_contents: VhdlFunctionContents) -> None:
        number_of_memory_instances = len(memory_instance_names)
        if number_of_memory_instances > 1:
            self._write_memory_instances(
                memory_name, number_of_memory_instances, memory_instance_names, function_contents=function_contents)
        else:
            memory_signal_name = memory_instance_names[0]
            self._write_memory_interface_signal_assignment(memory_master_name=memory_name, memory_slave_name=memory_signal_name,
                                                           function_contents=function_contents)

    def create_external_port_arbitration(self, function_contents: VhdlFunctionContents, external_port_name: str, memory_drivers: List[str]) -> None:
        self._write_memory_arbiter(memory_instance_names=memory_drivers, memory_name=external_port_name, function_contents=function_contents)
    
    def create_memory(self, function_contents: VhdlFunctionContents, memory_instance: VhdlMemory, memory_drivers: List[str]) -> None:
        self._write_memory_arbiter(memory_instance_names=memory_drivers, memory_name=memory_instance.name, function_contents=function_contents)

