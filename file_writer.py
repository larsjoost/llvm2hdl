from dataclasses import dataclass
import inspect
import io
import os
from typing import List, Tuple
from instance_data import DeclarationData, InstanceData
from instance_container_data import InstanceContainerData
from llvm_parser import ConstantDeclaration, InstructionArgument
from vhdl_declarations import VhdlDeclarations
from ports import Port
from messages import Messages

@dataclass
class Signal:
    instance : str
    name : str
    type : VhdlDeclarations
    def write_signal(self, file_handle):
        print("signal " + self.name + " : tag_t;", file=file_handle)
    def write_record_item(self, file_handle):
        print(self.instance + " : " + self.type.get_type_declarations() + ";", file=file_handle)
    def get_data_width(self) -> str:
        return self.type.get_data_width()

@dataclass
class Constant:
    constant : ConstantDeclaration
    def write_constant(self, file_handle):
        vhdl_declaration = VhdlDeclarations(self.constant.type)
        type_declaration = vhdl_declaration.get_type_declarations()
        initialization = vhdl_declaration.get_initialization(values=self.constant.get_values())
        name = self.constant.get_name()
        print("constant " + name + " : " + type_declaration + " := " + initialization + ";", file=file_handle)

class FileWriter:

    _debug : bool = False
    _file_name : str
    _header : List[str] = []
    _signals : List[Signal] = []
    _constants : List[Constant] = []
    _body : List[str] = []
    _trailer : List[str] = []
    _instances : List[str] = []

    def __init__(self, file_name: str):
        self._msg = Messages()
        self._file_name = file_name

    def _print_declarations(self, file_handle):
        total_data_width = [i.get_data_width() for i in self._signals]
        total_data_width.append("tag_width")
        print("constant c_tag_width : positive := " + " + ".join(total_data_width) + ";", file=file_handle)
        print("type tag_t is record", file=file_handle)
        print("tag : std_ulogic_vector(0 to tag_width - 1);", file=file_handle)
        for i in self._signals:
            i.write_record_item(file_handle=file_handle)
        print("end record;", file=file_handle)
        print("function conv_tag (", file=file_handle)
        print("arg : std_ulogic_vector(0 to c_tag_width - 1)) return tag_t is", file=file_handle)
        print("variable result_v : tag_t;", file=file_handle)
        print("begin", file=file_handle)
        record_items = [i.instance for i in self._signals]
        record_items.append("tag")
        assign_items = ["result_v." + i for i in record_items]
        print("(" + ", ".join(assign_items) + ") := arg;", file=file_handle)
        print("return result_v;", file=file_handle)
        print("end function conv_tag;", file=file_handle)
        print("function tag_to_std_ulogic_vector (", file=file_handle)
        print("arg : tag_t) return std_ulogic_vector is", file=file_handle)
        print("begin", file=file_handle)
        assign_arg = ["arg." + i for i in record_items]
        print("return " + " & ". join(assign_arg) + ";", file=file_handle)
        print("end function tag_to_std_ulogic_vector;", file=file_handle)
        for i in self._constants:
            i.write_constant(file_handle=file_handle)
        print("signal tag_in_i, tag_out_i : tag_t;", file=file_handle)
        for i in self._signals:
            i.write_signal(file_handle=file_handle)

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
        with open(self._file_name, 'w') as file_handle:
            self._print_header(file_handle=file_handle)
            self._print_declarations(file_handle=file_handle)
            print("begin", file=file_handle)
            self._print_body(file_handle=file_handle)
            self._print_trailer(file_handle=file_handle)
        instance_file_name = os.path.splitext(self._file_name)[0]+'.inc'
        with open(instance_file_name, 'w') as file_handle:
            for i in self._instances:
                print(i, file=file_handle)

    def _print_to_string(self, *args, **kwargs) -> str:
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        return contents
    
    def write_body(self, *args, **kwargs):
        if self._debug:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self._body.append(self._print_to_string(f"-- {file_name}:{line_number}:"))          
        self._body.append(self._print_to_string(*args, **kwargs))

    def write_header(self, *args, **kwargs):
        if self._debug:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self._header.append(self._print_to_string(f"-- {file_name}:{line_number}:"))          
        self._header.append(self._print_to_string(*args, **kwargs))

    def write_trailer(self, *args, **kwargs):
        if self._debug:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self._trailer.append(self._print_to_string(f"-- {file_name}:{line_number}:"))          
        self._trailer.append(self._print_to_string(*args, **kwargs))

    def _write_signal(self, declaration: DeclarationData):
        self._signals.append(Signal(instance=declaration.instance_name, name=declaration.entity_name, type=declaration.type))
    
    def _get_port_map(self, input_port: InstructionArgument) -> str:
        self._msg.function_start("_get_port_map(input_port=" + str(input_port) + ")", True)
        if input_port.single_dimension() and not input_port.is_pointer():
            dimensions: Tuple[int, str] = input_port.get_dimensions()
            result = "conv_std_ulogic_vector(" + input_port.get_signal_name() + ", " + dimensions[1] + ")"
        else:
            result = input_port.get_signal_name()
        if input_port.port_name is not None:
            result = input_port.port_name + " => " + result
        self._msg.function_end("_get_port_map = " + result, True)
        return result

    def _write_instance(self, instance: InstanceData):
        if instance.library != "work":
            self._instances.append(instance.entity_name)
        _input_ports = [self._get_port_map(input_port=i) for i in instance.input_ports] 
        block_name = instance.instance_name + "_b"
        local_tag_in = "local_tag_in_i"
        local_tag_out = "local_tag_out_i"
        self.write_body(f"{block_name} : block")
        self.write_body(f"signal {local_tag_in}, {local_tag_out} : std_ulogic_vector(0 to c_tag_width - 1);")
        self.write_body("signal q_i : " + instance.output_port.get_type_declarations() + ";")
        self.write_body("begin")
        self.write_body(f"{local_tag_in} <= tag_to_std_ulogic_vector(" + instance.previous_tag_name + ");")
        self.write_body(instance.instance_name + " : entity " + instance.library + "." + instance.entity_name)
        self.write_body("generic map (tag_width => c_tag_width) port map (", end="")
        self.write_body(", ".join(_input_ports), end="")
        self.write_body(", "+ instance.output_port.get_port_map(), end="")
        self.write_body(", clk => clk, sreset => sreset", end="")
        self.write_body(f", tag_in => {local_tag_in}", end="")
        self.write_body(f", tag_out => {local_tag_out}", end="")
        self.write_body(");")
        self.write_body("process (all)")
        self.write_body("begin")
        self.write_body(instance.tag_name + f" <= conv_tag({local_tag_out});")
        self.write_body(instance.tag_name + "." + instance.instance_name + " <= q_i;")
        self.write_body("end process;")
        self.write_body("end block " + block_name + ";")

    def _write_declaration(self, type: str, instances: List[str]):
        self.write_header(type + " (")
        self.write_header(";\n".join(instances))
        self.write_header(");")

    def _write_generics(self, generics: List[str]):
        self._write_declaration("generic", generics)
        
    def _get_port(self, port: Port) -> str:
        port_type: str = VhdlDeclarations(port.data_type).get_type_declarations()
        direction = "in" if port.is_input() else "out"
        return port.name + " : " + direction + " " + port_type

    def _write_ports(self, ports: List[Port]):
        self.write_header("port (")
        x = [self._get_port(i) for i in ports]
        self.write_header(";\n".join(x))
        self.write_header(");")

    def _write_instances(self, instances: InstanceContainerData):
        self.write_body("tag_in_i.tag <= tag_in;")
        for i in instances.instances:
            self._write_instance(instance=i)
        return_data_width: str = instances.get_return_data_width()
        self.write_body("return_value <= conv_std_ulogic_vector(tag_out_i." + instances.return_instruction_driver + ", " + return_data_width + ");")
        self.write_body("tag_out <= tag_out_i.tag;")

    def _write_declarations(self, declarations: List[DeclarationData]):
        for i in declarations:
            self._write_signal(declaration=i)

    def write_constant(self, constant: ConstantDeclaration):
        self._constants.append(Constant(constant))

    def write_function(self, entity_name: str, instances: InstanceContainerData, 
    declarations: List[DeclarationData], ports: List[Port], generics: List[str]):
        self.write_header("library ieee;")
        self.write_header("use ieee.std_logic_1164.all;")
        self.write_header("library llvm;")
        self.write_header("use llvm.llvm_pkg.conv_std_ulogic_vector;")
        self.write_header("use llvm.llvm_pkg.memory_i32;")
        self.write_header("use llvm.llvm_pkg.set_memory_i32;")
        self.write_header("library work;")
        self.write_header("entity " + entity_name + " is")
        self._write_generics(generics)
        self._write_ports(ports)
        self.write_header("begin")
        self.write_header("end entity " + entity_name + ";")
        self.write_header("architecture rtl of " + entity_name + " is")
        self._write_instances(instances=instances)
        self._write_declarations(declarations=declarations)
        self.write_trailer("end architecture rtl;")
        