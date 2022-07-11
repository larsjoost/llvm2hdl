from dataclasses import dataclass
import io
import os
from typing import List, Optional, Tuple
from instance_data import DeclarationData, InstanceData
from instance_container_data import InstanceContainerData
from llvm_parser import ConstantDeclaration
from vhdl_port import VhdlPortGenerator
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
        print("constant " + name + " : std_ulogic_vector := " + initialization + ";", file=file_handle)

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

    def __init__(self, file_name: str):
        self._msg = Messages()
        self._file_name = file_name

    def _print_total_data_width(self, file_handle) -> None:
        total_data_width = [i.get_data_width() for i in self._signals]
        total_data_width.append("s_tag'length")
        for i in self._ports:
            if i.is_input():
                total_data_width.append(i.get_name() + "'length")
        print("constant c_tag_width : positive := " + " + ".join(total_data_width) + ";", file=file_handle)

    def _print_tag_record(self, file_handle):
        print("type tag_t is record", file=file_handle)
        tag_elements = VhdlPortGenerator().get_tag_elements(ports=self._ports, signals=self._signals)
        for name, declaration in tag_elements:
            print(name + " " + declaration, file=file_handle)
        print("end record;", file=file_handle)
        
    def _print_function_conv_tag(self, file_handle, record_items: List[str]) -> None:
        assign_items = ["result_v." + i for i in record_items]
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
        assign_arg = ["arg." + i for i in record_items]
        print("return " + " & ". join(assign_arg) + ";", file=file_handle)
        print("end function tag_to_std_ulogic_vector;", file=file_handle)
        
    def _print_declarations(self, file_handle):
        self._print_total_data_width(file_handle=file_handle)
        self._print_tag_record(file_handle=file_handle)
        record_items = VhdlPortGenerator().get_tag_item_names(ports=self._ports, signals=self._signals)
        self._print_function_conv_tag(file_handle=file_handle, record_items=record_items)
        self._print_function_tag_to_std_ulogic_vector(record_items=record_items, file_handle=file_handle)
        for i in self._constants:
            i.write_constant(file_handle=file_handle)
        print("signal tag_in_i, tag_out_i : tag_t;", file=file_handle)
        for i in self._signals:
            i.write_signal(file_handle=file_handle)
        for i in self._instance_signals:
            print("signal " + i + ";", file=file_handle)

    def _print_list(self, file_handle, data: List[str]):
        for i in data:
            print(i, file=file_handle)

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
        instance_file_name = os.path.splitext(self._file_name)[0]+'.inc'
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

    def _write_instance(self, instance: InstanceData):
        if instance.library != "work":
            self._instances.append(instance.entity_name)
        vhdl_port = VhdlPortGenerator()
        self._instance_signals.extend(vhdl_port.get_standard_ports_signals(instance=instance))
        memory_ports = [i for i in instance.input_ports if i.is_pointer()]
        _memory_port_map = self._flatten([vhdl_port.get_memory_port_map(input_port=i) for i in memory_ports])
        _input_ports_map = [vhdl_port.get_port_map(input_port=i) for i in instance.input_ports]
        _input_ports_signals = [vhdl_port.get_port_signal(input_port=i) for i in instance.input_ports]
        _input_ports_signal_assignment = [vhdl_port.get_port_signal_assignment(input_port=i, ports=self._ports, signals=self._signals) for i in instance.input_ports]
        block_name = instance.instance_name + "_b"
        local_tag_in = "local_tag_in_i"
        local_tag_out = "local_tag_out_i"
        self._write_body(f"{block_name} : block")
        self._write_body("signal tag_i : tag_t;")
        self._write_body(f"signal {local_tag_in}, {local_tag_out} : std_ulogic_vector(0 to c_tag_width - 1);")
        for i in _input_ports_signals:
            self._write_body(i)
        self._write_body("signal m_tdata_i : " + instance.output_port.get_type_declarations() + ";")
        self._write_body("begin")
        tag_name = instance.get_previous_instance_signal_name("tag_out")
        self._write_body("tag_i <= " + ("tag_in_i" if tag_name is None else tag_name) + ";")
        self._write_body(f"{local_tag_in} <= tag_to_std_ulogic_vector(tag_i);")
        for i in _input_ports_signal_assignment:
            self._write_body(i)
        self._write_body(instance.instance_name + " : entity " + instance.library + "." + instance.entity_name)
        self._write_body("port map (", end="")
        self._write_body(", ".join(_input_ports_map), end="")
        if len(_memory_port_map) > 0:
            self._write_body(", " + ", ".join(_memory_port_map), end="")
        self._write_body(", "+ instance.output_port.get_port_map(), end="")
        self._write_body(", " + ", ".join(vhdl_port.get_standard_ports_map(instance=instance)), end="")
        self._write_body(f", s_tag => {local_tag_in}", end="")
        self._write_body(f", m_tag => {local_tag_out}", end="")
        self._write_body(");")
        self._write_body("process (all)")
        self._write_body("begin")
        self._write_body(instance.tag_name + f" <= conv_tag({local_tag_out});")
        self._write_body(instance.tag_name + "." + instance.instance_name + " <= m_tdata_i;")
        self._write_body("end process;")
        self._write_body("end block " + block_name + ";")

    def _get_ports(self, port: Port) -> List[str]:
        return VhdlPortGenerator().get_ports(port)

    def _write_ports(self, ports: List[Port]):
        self._write_header("port (")
        xss = [self._get_ports(i) for i in ports]
        x = self._flatten(xss) 
        standard_ports = VhdlPortGenerator().get_standard_ports_definition()
        tag_ports = ["s_tag : IN std_ulogic_vector", "m_tag : out std_ulogic_vector"] 
        self._write_header(";\n".join(x + standard_ports + tag_ports))
        self._write_header(");")

    def _write_instances(self, instances: InstanceContainerData):
        self._write_body("tag_in_i.tag <= s_tag;")
        for i in self._ports:
            if i.is_input():
                self._write_body("tag_in_i." + i.get_name() + " <= " + i.get_name() + ";")
        for i in instances.instances:
            self._write_instance(instance=i)
        return_driver = instances.get_return_instruction_driver()
        self._write_body("m_tvalid <= " + return_driver + "_m_tvalid_i;")
        self._write_body(return_driver + "_m_tready_i <= m_tready;")
        self._write_body("m_tdata <= conv_std_ulogic_vector(tag_out_i." + return_driver + ", m_tdata'length);")
        self._write_body("m_tag <= tag_out_i.tag;")

    def _write_declarations(self, declarations: List[DeclarationData]):
        for i in declarations:
            self._write_signal(declaration=i)

    def write_constant(self, constant: ConstantDeclaration):
        self._constants.append(Constant(constant))

    def write_function(self, entity_name: str, instances: InstanceContainerData,
    declarations: List[DeclarationData], ports: List[Port]):
        self._ports = ports
        self._write_header("library ieee;")
        self._write_header("use ieee.std_logic_1164.all;")
        self._write_header("library llvm;")
        self._write_header("use llvm.llvm_pkg.conv_std_ulogic_vector;")
        self._write_header("use llvm.llvm_pkg.get;")
        self._write_header("use llvm.llvm_pkg.integer_array_t;")
        self._write_header("library work;")
        self._write_header("entity " + entity_name + " is")
        self._write_ports(ports)
        self._write_header("begin")
        self._write_header("end entity " + entity_name + ";")
        self._write_header("architecture rtl of " + entity_name + " is")
        self._write_declarations(declarations=declarations)
        self._write_instances(instances=instances)
        self._write_trailer("end architecture rtl;")
        