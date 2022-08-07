from dataclasses import dataclass
import io
import os
from typing import List, Optional, Tuple
from function_definition import FunctionDefinition
from instance_data import DeclarationData, InstanceData
from instance_container_data import InstanceContainerData
from llvm_parser import ConstantDeclaration, InstructionArgument
from vhdl_port import VhdlMemoryPort, VhdlPortGenerator
from vhdl_declarations import VhdlDeclarations, VhdlSignal
from ports import Port
from messages import Messages

@dataclass
class Constant:
    constant : ConstantDeclaration
    def write_constant(self, file_handle):
        vhdl_declaration = VhdlDeclarations(self.constant.type)
        initialization = vhdl_declaration.get_initialization(values=self.constant.get_values())
        name = self.constant.get_name()
        print(f"constant {name} : std_ulogic_vector := {initialization};", file=file_handle)

class FileWriter:

    _debug : bool = False
    _file_name : str
    _header : List[str] = []
    _signals : List[VhdlSignal] = []
    _instance_signals: List[str] = []
    _constants : List[Constant] = []
    _body : List[str] = []
    _trailer : List[str] = []
    _instances : List[str] = []
    _ports: List[Port]

    _local_tag_in = "local_tag_in_i"
    _local_tag_out = "local_tag_out_i"
        
    def __init__(self, file_name: str):
        self._msg = Messages()
        self._file_name = file_name

    def _print_total_data_width(self, file_handle) -> None:
        total_data_width = [i.get_data_width() for i in self._signals]
        total_data_width.append("s_tag'length")
        total_data_width.extend([f"{i.get_name()}'length" for i in self._ports if i.is_input()])
        tag_width = " + ".join(total_data_width)
        print(f"constant c_tag_width : positive := {tag_width};", file=file_handle)

    def _print_tag_record(self, file_handle):
        print("type tag_t is record", file=file_handle)
        tag_elements = VhdlPortGenerator().get_tag_elements(ports=self._ports, signals=self._signals)
        for name, declaration in tag_elements:
            print(f"{name} {declaration}", file=file_handle)
        print("end record;", file=file_handle)
        
    def _print_function_conv_tag(self, file_handle, record_items: List[str]) -> None:
        assign_items = [f"result_v.{i}" for i in record_items]
        print("function conv_tag (", file=file_handle)
        print("arg : std_ulogic_vector(0 to c_tag_width - 1)) return tag_t is", file=file_handle)

        print("variable result_v : tag_t;", file=file_handle)
        print("begin", file=file_handle)
        print("(" + ", ".join(assign_items) + ") := arg;", file=file_handle)
        print("return result_v;", file=file_handle)
        print("end function conv_tag;", file=file_handle)
        
    def _print_function_tag_to_std_ulogic_vector(self, record_items: List[str], file_handle) -> None:
        print("function tag_to_std_ulogic_vector (", file=file_handle)
        print("arg : tag_t) return std_ulogic_vector is", file=file_handle)
        print("begin", file=file_handle)
        assign_arg = [f"arg.{i}" for i in record_items]
        print("return " + " & ".join(assign_arg) + ";", file=file_handle)
        print("end function tag_to_std_ulogic_vector;", file=file_handle)
        
    def _print_constants(self, file_handle):
        print("constant c_mem_addr_width : positive := 32;", file=file_handle)
        print("constant c_mem_data_width : positive := 32;", file=file_handle)
        print("constant c_mem_id_width : positive := 8;", file=file_handle)
        for i in self._constants:
            i.write_constant(file_handle=file_handle)
        
    def _print_signals(self, file_handle) -> None:
        print("signal tag_in_i, tag_out_i : tag_t;", file=file_handle)
        for signal in self._signals:
            signal.write_signal(file_handle=file_handle)
        for instance_signal in self._instance_signals:
            print(f"signal {instance_signal};", file=file_handle)

    def _print_declarations(self, file_handle):
        self._print_total_data_width(file_handle=file_handle)
        self._print_constants(file_handle=file_handle)
        self._print_tag_record(file_handle=file_handle)
        record_items = VhdlPortGenerator().get_tag_item_names(ports=self._ports, signals=self._signals)
        self._print_function_conv_tag(file_handle=file_handle, record_items=record_items)
        self._print_function_tag_to_std_ulogic_vector(record_items=record_items, file_handle=file_handle)
        self._print_signals(file_handle=file_handle)

    def _print_list(self, file_handle, data: List[str]):
        for i in data:
            print(i, file=file_handle, end="")

    def _print_header(self, file_handle):
        self._print_list(file_handle, self._header)

    def _print_body(self, file_handle):
        self._print_list(file_handle, self._body)

    def _print_trailer(self, file_handle):
        self._print_list(file_handle, self._trailer)

    def close(self):
        with open(self._file_name, 'w', encoding="utf-8") as file_handle:
            self._print_header(file_handle=file_handle)
            self._print_declarations(file_handle=file_handle)
            print("begin", file=file_handle)
            self._print_body(file_handle=file_handle)
            self._print_trailer(file_handle=file_handle)
        base_name = os.path.splitext(self._file_name)[0]
        instance_file_name = f'{base_name}.inc'
        with open(instance_file_name, 'w', encoding="utf-8") as file_handle:
            for i in self._instances:
                print(i, file=file_handle)

    def _print_to_string(self, *args, **kwargs) -> str:
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        return contents
    
    def _write_body(self, *args, **kwargs):
        self._body.append(self._print_to_string(*args, **kwargs))

    def _write_header(self, *args, **kwargs):
        self._header.append(self._print_to_string(*args, **kwargs))

    def _write_trailer(self, *args, **kwargs):
        self._trailer.append(self._print_to_string(*args, **kwargs))

    def _write_signal(self, declaration: DeclarationData):
        self._signals.append(VhdlSignal(instance=declaration.instance_name, 
        name=declaration.entity_name, type=declaration.type))

    def _flatten(self, xss: List[List[str]]) -> List[str]:
        return [x for xs in xss for x in xs]

    def _write_component_instantiation_generic_map(self, instance: InstanceData) -> None:
        if instance.generic_map is not None:
            self._write_body("generic map (")
            self._write_body("; ".join(instance.generic_map))
            self._write_body(")")

    def _get_component_instantiation_memory_port_map(self, instance: InstanceData) -> List[str]:
        self._msg.function_start(f"instance={instance}")
        vhdl_memory_port = VhdlMemoryPort()
        memory_port_map = []
        if instance.memory_interface is not None:
            master = instance.memory_interface.is_master()
            memory_port_map = vhdl_memory_port.get_port_map(name=instance.instance_name, master=master)
            self._instance_signals.extend(vhdl_memory_port.get_port_signals(name=instance.instance_name))
        self._msg.function_end(memory_port_map)
        return memory_port_map
 
    def _get_input_port_map(self, input_port: InstructionArgument, instance: InstanceData) -> List[str]:
        vhdl_port = VhdlPortGenerator()
        memory_interface_name = instance.get_memory_port_name(port=input_port)
        if memory_interface_name is not None:
            vhdl_memory_port = VhdlMemoryPort()
            self._instance_signals.extend(vhdl_memory_port.get_port_signals(name=memory_interface_name))
        return vhdl_port.get_port_map(input_port=input_port, memory_interface_name=memory_interface_name)

    def _get_input_port_maps(self, instance: InstanceData) -> List[str]:
        self._msg.function_start(f"instance={instance}")
        input_ports_map = [self._get_input_port_map(input_port=i, instance=instance) for i in instance.input_ports]
        result = self._flatten(input_ports_map)
        self._msg.function_end(result)
        return result

    def _write_component_instantiation_port_map(self, instance: InstanceData) -> None:
        self._msg.function_start(f"instance={instance}")
        vhdl_port = VhdlPortGenerator()
        memory_port_map = self._get_component_instantiation_memory_port_map(instance=instance)
        input_ports_map = self._get_input_port_maps(instance=instance)
        tag_port_map = [f"s_tag => {self._local_tag_in}", f"m_tag => {self._local_tag_out}"]
        standard_port_map =  vhdl_port.get_standard_ports_map(instance=instance)
        output_port_map = [] if instance.output_port.is_void() else vhdl_port.get_output_port_map(output_port=instance.output_port)
        ports = input_ports_map + output_port_map + memory_port_map + standard_port_map + tag_port_map
        self._write_body(", ".join(ports), end="")
        self._msg.function_end(None)

    def _write_component_instantiation(self, instance: InstanceData) -> None:
        self._msg.function_start(f"instance={instance}")
        self._write_body(f"{instance.instance_name} : entity {instance.library}.{instance.entity_name}")
        self._write_component_instantiation_generic_map(instance=instance)
        self._write_body("port map (", end="")
        self._write_component_instantiation_port_map(instance=instance)
        self._write_body(");")
        self._msg.function_end(None)

    def _write_component_output_signal_assignment(self, instance: InstanceData) -> None:
        self._msg.function_start(f"instance={instance}")
        self._write_body("process (all)")
        self._write_body("begin")
        self._write_body(f"{instance.tag_name} <= conv_tag({self._local_tag_out});")
        if not instance.output_port.is_void():
            self._write_body(f"{instance.tag_name}.{instance.instance_name} <= m_tdata_i;")
        self._write_body("end process;")
        self._msg.function_end(None)
        
    def _write_instance_signals(self, instance: InstanceData) -> None:
        vhdl_port = VhdlPortGenerator()
        input_ports_signals = [vhdl_port.get_port_signal(input_port=i) for i in instance.input_ports]
        self._write_body("signal tag_i : tag_t;")
        self._write_body(f"signal {self._local_tag_in}, {self._local_tag_out} : std_ulogic_vector(0 to c_tag_width - 1);")
        for i in input_ports_signals:
            self._write_body(i)
        self._write_body(f"signal m_tdata_i : {instance.output_port.get_type_declarations()};")

    def _write_instance_signal_assignments(self, instance: InstanceData) -> None:
        vhdl_port = VhdlPortGenerator()
        input_ports_signal_assignment = [vhdl_port.get_port_signal_assignment(input_port=i, ports=self._ports, signals=self._signals) for i in instance.input_ports]
        tag_name = instance.get_previous_instance_signal_name("tag_out")
        self._write_body("tag_i <= " + ("tag_in_i" if tag_name is None else tag_name) + ";")
        self._write_body(f"{self._local_tag_in} <= tag_to_std_ulogic_vector(tag_i);")
        for i in input_ports_signal_assignment:
            self._write_body(i)
    
    def _write_instance(self, instance: InstanceData) -> None:
        self._msg.function_start(f"instance={instance}")
        if instance.library != "work":
            self._instances.append(instance.entity_name)
        vhdl_port = VhdlPortGenerator()
        self._instance_signals.extend(vhdl_port.get_standard_ports_signals(instance=instance))
        block_name = f"{instance.instance_name}_b"
        self._write_body(f"{block_name} : block")
        self._write_instance_signals(instance=instance)
        self._write_body("begin")
        self._write_instance_signal_assignments(instance=instance)
        self._write_component_instantiation(instance=instance)
        self._write_component_output_signal_assignment(instance=instance)
        self._write_body(f"end block {block_name};")
        self._msg.function_end(None)

    def _get_ports(self, port: Port) -> List[str]:
        return VhdlPortGenerator().get_ports(port)

    def _write_ports(self, ports: List[Port]) -> None:
        self._write_header("port (")
        xss = [self._get_ports(i) for i in ports if not i.is_void()]
        x = self._flatten(xss) 
        standard_ports = VhdlPortGenerator().get_standard_ports_definition()
        tag_ports = ["s_tag : IN std_ulogic_vector", "m_tag : out std_ulogic_vector"] 
        self._write_header(";\n".join(x + standard_ports + tag_ports))
        self._write_header(");")

    def _write_instances(self, instances: InstanceContainerData, ports: List[Port]) -> None:
        self._msg.function_start(f"instances={instances}, ports={ports}")
        self._write_body("tag_in_i.tag <= s_tag;")
        for i in ports:
            if i.is_input():
                self._write_body(f"tag_in_i.{i.get_name()} <= {i.get_name()};")
        for j in instances.instances:
            self._write_instance(instance=j)
        return_driver = instances.get_return_instruction_driver()
        self._write_body(f"m_tvalid <= {return_driver}_m_tvalid_i;")
        self._write_body(f"{return_driver}_m_tready_i <= m_tready;")
        output_port_is_void = any((not i.is_input()) and i.is_void() for i in ports)
        if not output_port_is_void:
            self._write_body(f"m_tdata <= conv_std_ulogic_vector(tag_out_i.{return_driver}, m_tdata'length);")
        self._write_body("m_tag <= tag_out_i.tag;")
        self._msg.function_end(None)

    def _write_memory_arbiter_port_map(self, memory_master_name: str, memory_slave_name: str) -> None:
        vhdl_memory_port = VhdlMemoryPort()
        slave_memory_port_map = vhdl_memory_port.get_port_map(name=memory_slave_name, master=False)
        master_memory_port_map = vhdl_memory_port.get_port_map(name=memory_master_name, master=True)
        memory_port_map = slave_memory_port_map + master_memory_port_map
        self._write_body(", ".join(memory_port_map))

    def _write_memory_arbiter(self, instances: InstanceContainerData) -> None:
        for memory_name in instances.get_memory_names():
            vhdl_memory_port = VhdlMemoryPort()
            block_name = f"arbiter_{memory_name}_b"
            self._write_body(f"{block_name}: block")
            memory_instance_names = instances.get_memory_instance_names()
            number_of_memory_instances = len(memory_instance_names)
            self._write_body(f"constant c_size : positive := {number_of_memory_instances};")
            memory_signal_name = "s"
            signals = "\n".join([f"signal {i}; " for i in vhdl_memory_port.get_port_signals(name=memory_signal_name, scale_range="c_size")])
            self._write_body(signals)
            self._write_body("begin")
            signal_assigments = "\n".join([f"{i};" for i in vhdl_memory_port.get_signal_assignments(signal_name=memory_signal_name, assignment_names=memory_instance_names)])
            self._write_body(signal_assigments)
            memory_interface_name = f"memory_arbiter_{memory_name}"
            self._write_body(f"{memory_interface_name}: entity memory.arbiter(rtl)")
            self._write_body("port map(clk => clk, sreset => sreset,")
            self._write_memory_arbiter_port_map(memory_master_name=memory_name, memory_slave_name=memory_signal_name)
            self._write_body(");")
            self._write_body(f"end block {block_name};")

    def _write_declarations(self, declarations: List[DeclarationData]):
        for i in declarations:
            self._write_signal(declaration=i)

    def write_constant(self, constant: ConstantDeclaration):
        self._constants.append(Constant(constant))

    def _write_include_libraries(self) -> None:
        self._write_header("library ieee;")
        self._write_header("use ieee.std_logic_1164.all;")
        self._write_header("library llvm;")
        self._write_header("use llvm.llvm_pkg.conv_std_ulogic_vector;")
        self._write_header("use llvm.llvm_pkg.get;")
        self._write_header("use llvm.llvm_pkg.integer_array_t;")
        self._write_header("library memory;")
        self._write_header("library work;")
        
    def _write_entity(self, entity_name: str, ports: List[Port]) -> None:
        self._write_header(f"entity {entity_name} is")
        self._write_ports(ports=ports)
        self._write_header(f"end entity {entity_name};")
        
    def _write_architecture(self, function: FunctionDefinition) -> None:
        self._write_header(f"architecture rtl of {function.entity_name} is")
        self._write_declarations(declarations=function.declarations)
        self._write_instances(instances=function.instances, ports=function.ports)
        self._write_memory_arbiter(instances=function.instances)
        self._write_trailer("end architecture rtl;")

    def write_function(self, function: FunctionDefinition) -> None:
        self._msg.function_start(f"function={function}")
        self._ports = function.ports
        self._write_include_libraries()
        self._write_entity(entity_name=function.entity_name, ports=function.ports)
        self._write_architecture(function=function)
        self._msg.function_end(None)
        