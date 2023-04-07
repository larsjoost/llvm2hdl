import os
from types import FrameType
from typing import List, Optional
from file_writer_interface import FileWriterInterface
from llvm_constant import DeclarationBase
from llvm_function import LlvmFunctionContainer
from llvm_globals_container import GlobalsContainer
from signal_interface import SignalInterface
from vhdl_comment_generator import VhdlCommentGenerator
from vhdl_entity import VhdlEntity
from vhdl_function_container import FileWriterConstant, FileWriterReference, FileWriterVariable, VhdlFunctionContainer
from vhdl_function_contents import VhdlFunctionContents
from vhdl_function_definition import VhdlFunctionDefinition
from vhdl_generator import VhdlGenerator
from vhdl_include_libraries import VhdlIncludeLibraries
from vhdl_instance_container_data import VhdlInstanceContainerData
from vhdl_instance_data import VhdlDeclarationData, VhdlDeclarationDataContainer
from vhdl_instance_writer import VhdlInstanceWriter
from vhdl_port import VhdlMemoryPort, VhdlPortGenerator
from vhdl_declarations import VhdlDeclarations, VhdlSignal
from ports import PortContainer

class VhdlFunctionGenerator(FileWriterInterface):

    function_contents: VhdlFunctionContents
    container: VhdlFunctionContainer = VhdlFunctionContainer()

    def _get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        return VhdlCommentGenerator().get_comment(current_frame=current_frame)
        
    def _write_total_data_width(self, signals: List[SignalInterface], ports: PortContainer) -> None:
        total_data_width = [i.get_data_width() for i in signals]
        total_data_width.append("s_tag'length")
        total_data_width.extend(ports.get_total_input_data_width(generator=VhdlPortGenerator()))
        tag_width = " + ".join(total_data_width)
        self.function_contents.write_declaration(f"constant c_tag_width : positive := {tag_width};")
        
    def _write_tag_record(self) -> None:
        tag_elements = VhdlPortGenerator().get_tag_elements(ports=self.container.ports, signals=self.container.signals)
        record_elements = "\n".join(f"{name} {declaration}" for name, declaration in tag_elements)
        comment = VhdlCommentGenerator().get_comment() 
        self.function_contents.write_declaration(f"""
{comment}
type tag_t is record
{record_elements}
end record;
        """)
        
    def _write_function_conv_tag(self, record_items: List[str]) -> None:
        assign_items = ", ".join([f"result_v.{i}" for i in record_items])
        comment = VhdlCommentGenerator().get_comment() 
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
        comment = VhdlCommentGenerator().get_comment() 
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
        
    def _write_signal(self, declaration: VhdlDeclarationData) -> None:
        self.container.signals.append(VhdlSignal(instance=declaration.instance_name, 
        name=declaration.declaration_name, type=VhdlDeclarations(data_type=declaration.data_type)))

    def _get_memory_arbiter_port_map(self, memory_master_name: str, memory_slave_name: str) -> str:
        vhdl_memory_port = VhdlMemoryPort()
        slave_memory_port_map = vhdl_memory_port.get_port_map(name=memory_slave_name, master=False)
        master_memory_port_map = vhdl_memory_port.get_port_map(name=memory_master_name, master=True)
        memory_port_map = slave_memory_port_map + master_memory_port_map
        return ", ".join(memory_port_map)

    def _write_memory_interface_signal_assignment(self, memory_master_name: str, memory_slave_name: str) -> None:
        vhdl_memory_port = VhdlMemoryPort()
        assignment_list = vhdl_memory_port.get_signal_assignments(signal_name=memory_master_name, assignment_names=[memory_slave_name])
        assignments = "\n".join([f"{i};" for i in assignment_list])
        self.function_contents.write_body(assignments)
        
    def _write_memory_arbiter(self, instances: VhdlInstanceContainerData, memory_name: str) -> None:
        memory_instance_names = instances.get_memory_instance_names()
        number_of_memory_instances = len(memory_instance_names)
        if number_of_memory_instances > 1:
            self._write_memory_instances(
                memory_name, number_of_memory_instances, memory_instance_names
            )
        else:
            memory_signal_name = memory_instance_names[0]
            self._write_memory_interface_signal_assignment(memory_master_name=memory_name, memory_slave_name=memory_signal_name)
        
    def _write_memory_instances(self, memory_name: str, number_of_memory_instances: int, memory_instance_names: List[str]):
        memory_signal_name = "s"
        vhdl_memory_port = VhdlMemoryPort()
        block_name = f"arbiter_{memory_name}_b"
        signals = "\n".join([f"signal {i}; " for i in vhdl_memory_port.get_port_signals(name=memory_signal_name, scale_range="c_size")])
        signal_assigment_list = vhdl_memory_port.get_signal_assignments(signal_name=memory_signal_name, assignment_names=memory_instance_names)
        signal_assigments = "\n".join([f"{i};" for i in signal_assigment_list])
        memory_interface_name = f"memory_arbiter_{memory_name}"
        port_map = self._get_memory_arbiter_port_map(memory_master_name=memory_name, memory_slave_name=memory_signal_name)
        comment = VhdlCommentGenerator().get_comment() 
        self.function_contents.write_body(f"""
{comment}
{block_name}: block
constant c_size : positive := {number_of_memory_instances};
{signals}
begin

{signal_assigments}
        
{memory_interface_name}: entity memory.arbiter(rtl)
port map(
clk => clk, 
sreset => sreset,
{port_map}
);

end block {block_name};

        """)

    def _write_all_memory_arbiters(self, instances: VhdlInstanceContainerData, memory_port_names: List[str]) -> None:
        for memory_name in instances.get_memory_names() + memory_port_names:
            self._write_memory_arbiter(instances=instances, memory_name=memory_name)
        
    def _write_declarations(self, declarations: VhdlDeclarationDataContainer):
        for i in declarations.declarations:
            self._write_signal(declaration=i)

    def write_constant(self, constant: DeclarationBase):
        self.container.constants.append(FileWriterConstant(constant=constant))

    def write_reference(self, reference: DeclarationBase, functions: LlvmFunctionContainer):
        self.container.references.append(FileWriterReference(reference=reference, functions=functions))

    def write_variable(self, variable: DeclarationBase):
        self.container.variables.append(FileWriterVariable(variable=variable))

    def _write_include_libraries(self) -> None:
        self.function_contents.write_header(VhdlIncludeLibraries().get())
        
    def _write_architecture(self, function: VhdlFunctionDefinition, globals: GlobalsContainer) -> None:
        self._write_declarations(declarations=function.declarations)
        generator = VhdlGenerator(contents=self.function_contents)
        VhdlInstanceWriter().write_instances(function=function, generator=generator, container=self.container)
        generator.generate_code(function_contents=self.function_contents, container=self.container, globals=globals)
        self._write_all_memory_arbiters(instances=function.instances, memory_port_names=function.get_memory_port_names())
        
    def write_function(self, function: VhdlFunctionDefinition, globals: GlobalsContainer) -> VhdlFunctionContents:
        self.function_contents = VhdlFunctionContents(name=function.entity_name)    
        self.container.ports = function.ports
        self.function_contents.write_header(f"-- Autogenerated by {self._get_comment()}")
        self._write_include_libraries()
        self.function_contents.write_header(VhdlEntity().get_entity(entity_name=function.entity_name, ports=function.ports))
        self._write_architecture(function=function, globals=globals)
        self._write_declarations_to_header()
        self._write_references_to_trailer()
        return self.function_contents

class FilePrinter:

    def generate(self, file_name: str, contents: List[VhdlFunctionContents]) -> None:
        with open(file_name, 'w', encoding="utf-8") as file_handle:
            for i in contents:
                print(i.get_contents(), file=file_handle, end="")
        base_name = os.path.splitext(file_name)[0]
        instance_file_name = f'{base_name}.inc'
        with open(instance_file_name, 'w', encoding="utf-8") as file_handle:
            for i in contents:
                print(i.get_instances(), file=file_handle)

