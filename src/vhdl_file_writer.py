import os
from types import FrameType
from typing import List, Optional
from file_writer_interface import FileWriterInterface
from llvm_constant import DeclarationBase
from llvm_function import LlvmFunction, LlvmFunctionContainer
from llvm_globals_container import GlobalsContainer
from llvm_module import LlvmModule
from signal_interface import SignalInterface
from vhdl_code_generator import VhdlCodeGenerator
from vhdl_entity import VhdlEntity
from vhdl_function import VhdlFunction
from vhdl_function_container import FileWriterConstant, FileWriterReference, FileWriterVariable, VhdlFunctionContainer
from vhdl_function_contents import VhdlFunctionContents
from vhdl_function_definition import VhdlFunctionDefinition
from vhdl_generator import VhdlGenerator
from vhdl_include_libraries import VhdlIncludeLibraries
from vhdl_instance_writer import VhdlInstanceWriter
from vhdl_memory_generator import VhdlMemoryGenerator
from vhdl_module import VhdlModule
from vhdl_port import VhdlPortGenerator
from ports import PortContainer

class VhdlFunctionGenerator(FileWriterInterface):

    function_contents: VhdlFunctionContents
    container: VhdlFunctionContainer = VhdlFunctionContainer()

    def _get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        return VhdlCodeGenerator().get_comment(current_frame=current_frame)
        
    def _write_total_data_width(self, signals: List[SignalInterface], ports: PortContainer) -> None:
        total_data_width = [i.get_data_width() for i in signals]
        total_data_width.append("s_tag'length")
        total_data_width.extend(ports.get_total_input_data_width(generator=VhdlPortGenerator()))
        tag_width = " + ".join(total_data_width)
        self.function_contents.write_declaration(f"constant c_tag_width : positive := {tag_width};")
        
    def _write_tag_record(self) -> None:
        tag_elements = VhdlPortGenerator().get_tag_elements(ports=self.container.ports, signals=self.container.signals)
        record_elements = "\n".join(f"{name} {declaration}" for name, declaration in tag_elements)
        comment = VhdlCodeGenerator().get_comment() 
        self.function_contents.write_declaration(f"""
{comment}
type tag_t is record
{record_elements}
end record;
        """)
        
    def _write_function_conv_tag(self, record_items: List[str]) -> None:
        assign_items = ", ".join([f"result_v.{i}" for i in record_items])
        comment = VhdlCodeGenerator().get_comment() 
        self.function_contents.write_declaration(f"""
{comment}
function conv_tag (
  arg : std_ulogic_vector(0 to c_tag_width - 1)) return tag_t is
  variable result_v : tag_t;
begin
  ({assign_items}) := arg;
  return result_v;
end function conv_tag;

    """)
        
    def _write_function_tag_to_std_ulogic_vector(self, record_items: List[str]) -> None:
        assign_arg = " & ".join([f"arg.{i}" for i in record_items])
        comment = VhdlCodeGenerator().get_comment() 
        self.function_contents.write_declaration(f"""
{comment}        
function tag_to_std_ulogic_vector (
  arg : tag_t) return std_ulogic_vector is
begin
  return {assign_arg};
end function tag_to_std_ulogic_vector;

        """)
        
    def _write_constants(self, constants: List[FileWriterConstant]) -> None:
        default_constants = [("c_mem_addr_width", 32), ("c_mem_data_width", 32), ("c_mem_id_width", 8)]
        for name, width in default_constants:
            self.function_contents.write_declaration(f"constant {name} : positive := {width};")
        for i in constants:
            self.function_contents.write_declaration(i.write_constant())
        
    def _write_references(self, references: List[FileWriterReference]) -> None:
        for i in references:
            self.function_contents.write_trailer(i.write_reference())

    def _write_variables(self, variables: List[FileWriterVariable]) -> None:
        for i in variables:
            self.function_contents.write_declaration(i.write_variable())

    def _write_signals(self) -> None:
        self.function_contents.write_declaration("signal tag_in_i, tag_out_i : tag_t;")
        signal_declaration = "\n".join(signal.get_signal_declaration() for signal in self.container.signals)
        self.function_contents.write_declaration(signal_declaration)
        signals = self.container.instance_signals.get_signals()
        self.function_contents.write_declaration(signals)

    def _write_declarations_to_header(self) -> None:
        self._write_variables(variables=self.container.variables)
        self._write_constants(constants=self.container.constants)
        self._write_total_data_width(signals=self.container.signals, ports=self.container.ports)
        self._write_tag_record()
        record_items = VhdlPortGenerator().get_tag_item_names(ports=self.container.ports, signals=self.container.signals)
        self._write_function_conv_tag(record_items=record_items)
        self._write_function_tag_to_std_ulogic_vector(record_items=record_items)
        self._write_signals()
        
    def _write_references_to_trailer(self) -> None:
        self._write_references(references=self.container.references)
        
    def write_constant(self, constant: DeclarationBase):
        self.container.constants.append(FileWriterConstant(constant=constant))

    def write_reference(self, reference: DeclarationBase, functions: LlvmFunctionContainer):
        self.container.references.append(FileWriterReference(reference=reference, functions=functions))

    def write_variable(self, variable: DeclarationBase):
        self.container.variables.append(FileWriterVariable(variable=variable))

    def _write_include_libraries(self) -> None:
        self.function_contents.write_header(VhdlIncludeLibraries().get())
        
    def _write_architecture(self, function: VhdlFunction, module: VhdlModule) -> None:
        VhdlInstanceWriter().write_instances(function=function, function_contents=self.function_contents, container=self.container, module=module)
        
    def write_function(self, function: VhdlFunction, module: VhdlModule) -> VhdlFunctionContents:
        self.function_contents = VhdlFunctionContents(name=function.get_entity_name())    
        self.container.ports = function.get_ports()
        self.function_contents.write_header(f"-- Autogenerated by {self._get_comment()}")
        self._write_include_libraries()
        self.function_contents.write_header(VhdlEntity().get_entity(entity_name=function.get_entity_name(), ports=function.get_ports()))
        self._write_architecture(function=function, module=module)
        self._write_declarations_to_header()
        self._write_references_to_trailer()
        return self.function_contents
