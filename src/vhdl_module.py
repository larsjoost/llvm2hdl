
from dataclasses import dataclass
from types import FrameType
from typing import List, Optional
from llvm_destination import LlvmDestination
from llvm_function import LlvmFunction

from llvm_module import LlvmModule
from ports import PortContainer
from signal_interface import SignalInterface
from vhdl_code_generator import VhdlCodeGenerator
from vhdl_entity import VhdlEntity
from vhdl_function import VhdlFunction
from vhdl_function_container import VhdlFileWriterReference, VhdlFileWriterVariable
from vhdl_file_writer_constant import VhdlFileWriterConstant
from vhdl_function_contents import VhdlFunctionContents
from vhdl_include_libraries import VhdlIncludeLibraries
from vhdl_instance_writer import VhdlInstanceWriter
from vhdl_memory import VhdlMemory
from vhdl_memory_generator import VhdlMemoryGenerator
from vhdl_port_generator import VhdlPortGenerator

@dataclass
class VhdlModule:
    module: LlvmModule

    def get_external_pointer_names(self) -> List[str]:
        return self.module.get_external_pointer_names()
    
    def _get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        return VhdlCodeGenerator().get_comment(current_frame=current_frame)
        
    def _write_total_data_width(self, function_contents: VhdlFunctionContents, signals: List[SignalInterface], ports: PortContainer) -> None:
        total_data_width = [i.get_data_width() for i in signals]
        total_data_width.append("s_tag'length")
        total_data_width.extend(ports.get_total_input_data_width(generator=VhdlPortGenerator()))
        tag_width = " + ".join(total_data_width)
        function_contents.write_declaration(f"constant c_tag_width : positive := {tag_width};")
        
    def _write_tag_record(self, function_contents: VhdlFunctionContents) -> None:
        tag_elements = VhdlPortGenerator().get_tag_elements(ports=function_contents.get_ports(), signals=function_contents.get_signals())
        record_elements = "\n".join(f"{name} {declaration}" for name, declaration in tag_elements)
        comment = VhdlCodeGenerator().get_comment() 
        function_contents.write_declaration(f"""
{comment}
type tag_t is record
{record_elements}
end record;
        """)
        
    def _write_function_conv_tag(self, function_contents: VhdlFunctionContents, record_items: List[str]) -> None:
        assign_items = ", ".join([f"result_v.{i}" for i in record_items])
        comment = VhdlCodeGenerator().get_comment() 
        function_contents.write_declaration(f"""
{comment}
function conv_tag (
  arg : std_ulogic_vector(0 to c_tag_width - 1)) return tag_t is
  variable result_v : tag_t;
begin
  ({assign_items}) := arg;
  return result_v;
end function conv_tag;

    """)
        
    def _write_function_tag_to_std_ulogic_vector(self, function_contents: VhdlFunctionContents, record_items: List[str]) -> None:
        assign_arg = " & ".join([f"arg.{i}" for i in record_items])
        comment = VhdlCodeGenerator().get_comment() 
        function_contents.write_declaration(f"""
{comment}        
function tag_to_std_ulogic_vector (
  arg : tag_t) return std_ulogic_vector is
begin
  return {assign_arg};
end function tag_to_std_ulogic_vector;

        """)
        
    def _write_constant_memory(self, function_contents: VhdlFunctionContents, constant: VhdlFileWriterConstant) -> None:
        function_contents.write_declaration(constant.get_constant_declaration())
        memory = constant.get_memory_instance()
        function_contents.write_declaration(memory.get_memory_signals())
        function_contents.write_body(memory.get_memory_instance())

    def _write_constants(self, function_contents: VhdlFunctionContents, constants: List[VhdlFileWriterConstant]) -> None:
        default_constants = [("c_mem_addr_width", 32), ("c_mem_data_width", 32), ("c_mem_id_width", 8)]
        for name, width in default_constants:
            function_contents.write_declaration(f"constant {name} : positive := {width};")
        for i in constants:
            self._write_constant_memory(function_contents=function_contents, constant=i)

    def _write_references(self, function_contents: VhdlFunctionContents, references: List[VhdlFileWriterReference]) -> None:
        for i in references:
            function_contents.write_trailer(i.write_reference())

    def _write_variables(self, function_contents: VhdlFunctionContents, variables: List[VhdlFileWriterVariable]) -> None:
        for i in variables:
            function_contents.write_declaration(i.write_variable())

    def _write_signals(self, function_contents: VhdlFunctionContents) -> None:
        function_contents.write_declaration("signal tag_in_i, tag_out_i : tag_t;")
        signals = function_contents.get_instance_signals()
        function_contents.write_declaration(signals)

    def _write_declarations_to_header(self, function_contents: VhdlFunctionContents) -> None:
        self._write_variables(function_contents=function_contents, variables=function_contents.get_variables())
        constants = [VhdlFileWriterConstant(i) for i in self.module.get_constants()]
        self._write_constants(function_contents=function_contents, constants=constants)
        self._write_total_data_width(function_contents=function_contents, signals=function_contents.get_signals(), ports=function_contents.get_ports())
        self._write_tag_record(function_contents=function_contents)
        record_items = VhdlPortGenerator().get_tag_item_names(ports=function_contents.get_ports(), signals=function_contents.get_signals())
        self._write_function_conv_tag(function_contents=function_contents, record_items=record_items)
        self._write_function_tag_to_std_ulogic_vector(function_contents=function_contents, record_items=record_items)
        self._write_signals(function_contents=function_contents)
        
    def _write_references_to_trailer(self, function_contents: VhdlFunctionContents) -> None:
        self._write_references(function_contents=function_contents, references=function_contents.get_references())
        
    def _write_include_libraries(self, function_contents: VhdlFunctionContents) -> None:
        function_contents.write_header(VhdlIncludeLibraries().get())
        
    def _write_external_memory_arbitration(self, function_contents: VhdlFunctionContents, function: VhdlFunction, external_port_name: str) -> None:
        memory_drivers = function.get_pointer_drivers(pointer_name=external_port_name)
        vhdl_memory_generator = VhdlMemoryGenerator()
        vhdl_memory_generator.create_external_port_arbitration(function_contents=function_contents, external_port_name=external_port_name, memory_drivers=memory_drivers)
        
    def _write_architecture(self, function_contents: VhdlFunctionContents, function: VhdlFunction) -> None:
        external_pointer_names = function.get_external_pointer_names()
        globals = self.module.get_globals()
        VhdlInstanceWriter().write_instances(function=function, function_contents=function_contents, 
                                             external_pointer_names=external_pointer_names, globals=globals)
        for external_port_name in external_pointer_names:
            self._write_external_memory_arbitration(function_contents=function_contents, function=function, external_port_name=external_port_name)

    def _write_function(self, function_contents: VhdlFunctionContents, function: VhdlFunction):
        function_contents.container.ports = function.get_ports()
        function_contents.write_header(f"-- Autogenerated by {self._get_comment()}")
        self._write_include_libraries(function_contents=function_contents)
        function_contents.write_header(VhdlEntity().get_entity(entity_name=function.get_entity_name(), ports=function.get_ports()))
        self._write_architecture(function_contents=function_contents, function=function)
        self._write_declarations_to_header(function_contents=function_contents)
        self._write_references_to_trailer(function_contents=function_contents)

    def _write_globals(self, function_contents: VhdlFunctionContents) -> None:
        for reference in self.module.get_references():
            function_contents.add_reference(VhdlFileWriterReference(reference=reference, functions=self.module.functions))
        for variable in self.module.get_variables():
            function_contents.add_variable(VhdlFileWriterVariable(variable=variable))

    def _get_memory_drivers(self, memory_instance: VhdlMemory) -> List[str]:
        memory_drivers = self.module.get_pointer_drivers(pointer_name=memory_instance.name)
        vhdl_code_generator = VhdlCodeGenerator()
        return [vhdl_code_generator.get_vhdl_name(i) for i in memory_drivers]

    def _write_memory_instance(self, function_contents: VhdlFunctionContents, memory_instance: VhdlMemory) -> None:
        memory_drivers = self._get_memory_drivers(memory_instance=memory_instance)
        vhdl_memory_generator = VhdlMemoryGenerator()
        vhdl_memory_generator.create_memory(function_contents=function_contents, memory_instance=memory_instance, memory_drivers=memory_drivers)

    def _write_memory(self, function_contents: VhdlFunctionContents) -> None:
        memory_instances: List[VhdlMemory] = self.module.get_memory_instances()
        for memory_instance in memory_instances:
            self._write_memory_instance(function_contents=function_contents, memory_instance=memory_instance)

    def _write_pointer_arbiter(self, function_contents: VhdlFunctionContents, pointer_destination: LlvmDestination) -> None:
        pointer_name = pointer_destination.get_translated_name()
        pointer_drivers = self.module.get_pointer_drivers(pointer_name=pointer_name)
        vhdl_memory_generator = VhdlMemoryGenerator()
        vhdl_memory_generator.write_memory_arbiter(function_contents=function_contents, memory_drivers=pointer_drivers, pointer_name=pointer_name)

    def _write_pointer_arbiters(self, function_contents: VhdlFunctionContents, function: LlvmFunction) -> None:
        pointer_destinations: List[LlvmDestination] = function.get_pointer_destinations()
        for pointer_destination in pointer_destinations:
            self._write_pointer_arbiter(function_contents=function_contents, pointer_destination=pointer_destination)        

    def _generate_function(self, function: LlvmFunction) -> VhdlFunctionContents:
        vhdl_function = VhdlFunction(function=function)
        function_contents = VhdlFunctionContents(name=vhdl_function.get_entity_name())    
        self._write_globals(function_contents=function_contents)
        self._write_function(function_contents=function_contents, function=vhdl_function)    
        self._write_memory(function_contents=function_contents)
        self._write_pointer_arbiters(function_contents=function_contents, function=function)
        return function_contents

    def generate_code(self) -> List[VhdlFunctionContents]:
        file_contents: List[VhdlFunctionContents] = [
            self._generate_function(function=function)
            for function in self.module.functions.functions
        ]
        return file_contents
 
