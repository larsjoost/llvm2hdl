
from dataclasses import dataclass, field
import inspect
import io
import os
from types import FrameType
from typing import List, Optional
from file_writer_interface import FileWriterInterface
from frame_info import FrameInfoFactory
from llvm_constant import DeclarationBase
from llvm_function import LlvmFunction, LlvmFunctionContainer
from vhdl_entity import VhdlEntity
from vhdl_function_definition import VhdlFunctionDefinition
from vhdl_include_libraries import VhdlIncludeLibraries
from vhdl_instance_container_data import VhdlInstanceContainerData
from vhdl_instance_data import VhdlDeclarationData, VhdlDeclarationDataContainer, VhdlInstanceData
from vhdl_instruction_argument import VhdlInstructionArgument
from vhdl_port import VhdlMemoryPort, VhdlPortGenerator
from vhdl_declarations import VhdlDeclarations, VhdlSignal
from ports import PortContainer

class CommentGenerator:
    def get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        if current_frame is None:
            current_frame = inspect.currentframe()
        frame_info = FrameInfoFactory().get_frame_info(current_frame=current_frame)
        assert frame_info.file_name is not None
        file_name = os.path.basename(frame_info.file_name)
        return f"-- {file_name}({frame_info.line_number}): "

@dataclass
class FileWriterConstant:
    constant : DeclarationBase
    def write_constant(self) -> str:
        data_type = self.constant.get_type()
        assert data_type is not None
        vhdl_declaration = VhdlDeclarations(data_type=data_type)
        values = self.constant.get_values()
        if values is None:
            return ""
        initialization = vhdl_declaration.get_initialization(values=values)
        name = self.constant.get_name()
        return f"constant {name} : std_ulogic_vector := {initialization};"

@dataclass
class FileWriterReference:
    reference : DeclarationBase
    functions: LlvmFunctionContainer
    def _get_reference(self, comment: str, include_libraries: str, entity: str, 
                       architecture: str, entity_reference: str, port_map: str) -> str:
        return f"""
{comment} References

{include_libraries}

{entity}

architecture rtl of {architecture} is
begin
  {entity_reference}_1: entity work.{entity_reference}(rtl)
  port map (
{port_map}
  );
end architecture rtl;
        """

    def _get_port_map(self, ports: PortContainer) -> str:
        vhdl_entity = VhdlEntity()
        port_names: List[str] = vhdl_entity.get_port_names(ports=ports)
        return ", ".join([f"{i} => {i}" for i in port_names])

    def _get_ports(self, reference : DeclarationBase) -> PortContainer:
        reference_name = reference.get_reference()
        assert reference_name is not None
        function: Optional[LlvmFunction] = self.functions.get_function(name=reference_name)
        instantiation_point = reference.instantiation_point.show()
        instruction = reference.instruction.get_elaborated()
        function_names = ", ".join(self.functions.get_function_names())
        assert function is not None, f'Could not find function reference {reference_name} among the following functions {function_names} in "{instruction}" instantiated at {instantiation_point}'
        return function.get_ports()
       
    def write_reference(self) -> str:
        comment = CommentGenerator().get_comment(current_frame=inspect.currentframe())
        vhdl_entity = VhdlEntity()
        name = vhdl_entity.get_entity_name(self.reference.get_name())
        reference = self.reference.get_reference()
        assert reference is not None
        entity_reference = vhdl_entity.get_entity_name(name=reference)
        ports: PortContainer = self._get_ports(reference=self.reference)
        entity = vhdl_entity.get_entity(entity_name=name, ports=ports)
        port_map = self._get_port_map(ports=ports)
        include_libraries = VhdlIncludeLibraries().get()
        return self._get_reference(comment=comment, include_libraries=include_libraries, 
        entity=entity, architecture=name, entity_reference=entity_reference, port_map=port_map)
        
@dataclass
class FileWriterVariable:
    variable : DeclarationBase
    def write_variable(self) -> str:
        comment = CommentGenerator().get_comment() 
        name = self.variable.get_name()
        data_width = self.variable.get_data_width()
        return f"""
{comment} Global variables
signal {name} : std_ulogic_vector(0 to {data_width} - 1);
        """

@dataclass
class FunctionContents:
    header : List[str] =  field(default_factory=list) 
    body : List[str]  =  field(default_factory=list)
    trailer : List[str]  =  field(default_factory=list)
    instances : List[str]  =  field(default_factory=list)
    
    def get_description(self, text: str) -> List[str]:
        return [f"""

--------------------------------------------------------------------------------
-- {text}
--------------------------------------------------------------------------------

        """]

    def get_contents(self) -> str:
        return "".join(self.get_description("Header") + self.header + 
        self.get_description("Body") + self.body + 
        self.get_description("Trailer") + self.trailer)
    def get_instances(self) -> str:
        return "\n".join(self.instances)
    def ___str__(self) -> str:
        return self.get_contents()
    def __repr__(self) -> str:
        return self.get_contents()

@dataclass
class Signals:
    comment : str
    signals : List[str]
    
class InstanceSignals:
    signals: List[Signals]
    def __init__(self) -> None:
        self.signals = []
    def get_signals(self) -> str:
        result = ""
        for i in self.signals:
            result += "\n" + i.comment + "\n"
            result += "\n".join(f"signal {instance_signal};" for instance_signal in i.signals)
        return result
    def add(self, signals: List[str]) -> None:
        comment = CommentGenerator().get_comment(current_frame=inspect.currentframe())
        self.signals.append(Signals(comment=comment, signals=signals))

@dataclass
class VhdlFunctionContainer:
    signals : List[VhdlSignal] = field(default_factory=list)
    instance_signals: InstanceSignals = field(default_factory=lambda : InstanceSignals())
    constants : List[FileWriterConstant] = field(default_factory=list)
    references: List[FileWriterReference] = field(default_factory=list)
    variables: List[FileWriterVariable] = field(default_factory=list)
    ports: PortContainer = field(default_factory=lambda : PortContainer())
 
@dataclass
class VhdlFunctionGenerator(FileWriterInterface):

    function_contents: FunctionContents = field(default_factory=lambda : FunctionContents())
    container: VhdlFunctionContainer = field(default_factory=lambda : VhdlFunctionContainer())

    _local_tag_in: str = "local_tag_in_i"
    _local_tag_out: str = "local_tag_out_i"
        
    def _get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        return CommentGenerator().get_comment(current_frame=current_frame)
        
    def _write_total_data_width(self, signals: List[VhdlSignal], ports: PortContainer) -> None:
        total_data_width = [i.get_data_width() for i in signals]
        total_data_width.append("s_tag'length")
        total_data_width.extend(ports.get_total_input_data_width(generator=VhdlPortGenerator()))
        tag_width = " + ".join(total_data_width)
        self._write_header(f"constant c_tag_width : positive := {tag_width};")
        
    def _write_tag_record(self) -> None:
        tag_elements = VhdlPortGenerator().get_tag_elements(ports=self.container.ports, signals=self.container.signals)
        record_elements = "\n".join(f"{name} {declaration}" for name, declaration in tag_elements)
        self._write_header(f"""
type tag_t is record
{record_elements}
end record;
        """)
        
    def _write_function_conv_tag(self, record_items: List[str]) -> None:
        assign_items = ", ".join([f"result_v.{i}" for i in record_items])
        self._write_header(f"""

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
        self._write_header(f"""
        
function tag_to_std_ulogic_vector (
  arg : tag_t) return std_ulogic_vector is
begin
  return {assign_arg};
end function tag_to_std_ulogic_vector;

        """)
        
    def _write_constants(self, constants: List[FileWriterConstant]) -> None:
        default_constants = [("c_mem_addr_width", 32), ("c_mem_data_width", 32), ("c_mem_id_width", 8)]
        for name, width in default_constants:
            self._write_header(f"constant {name} : positive := {width};")
        for i in constants:
            self._write_header(i.write_constant())
        
    def _write_references(self, references: List[FileWriterReference]) -> None:
        for i in references:
            self._write_trailer(i.write_reference())

    def _write_variables(self, variables: List[FileWriterVariable]) -> None:
        for i in variables:
            self._write_header(i.write_variable())

    def _write_signals(self) -> None:
        self._write_header("signal tag_in_i, tag_out_i : tag_t;")
        signal_declaration = "\n".join(signal.get_signal_declaration() for signal in self.container.signals)
        self._write_header(signal_declaration)
        signals = self.container.instance_signals.get_signals()
        self._write_header(signals)

    def _write_declarations_to_header(self) -> None:
        self._write_variables(variables=self.container.variables)
        self._write_total_data_width(signals=self.container.signals, ports=self.container.ports)
        self._write_constants(constants=self.container.constants)
        self._write_tag_record()
        record_items = VhdlPortGenerator().get_tag_item_names(ports=self.container.ports, signals=self.container.signals)
        self._write_function_conv_tag(record_items=record_items)
        self._write_function_tag_to_std_ulogic_vector(record_items=record_items)
        self._write_signals()
        self._write_header("begin")

    def _write_references_to_trailer(self) -> None:
        self._write_references(references=self.container.references)
        
    def _print_to_string(self, *args, **kwargs) -> str:
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        return contents
    
    def _write_body(self, *args, **kwargs):
        content = self._print_to_string(*args, **kwargs)
        comment = self._get_comment(current_frame=inspect.currentframe())
        self.function_contents.body.append(f"{comment}\n{content}")

    def _write_header(self, *args, **kwargs):
        content = self._print_to_string(*args, **kwargs)
        comment = self._get_comment(current_frame=inspect.currentframe())
        self.function_contents.header.append(f"{comment}\n{content}")

    def _write_trailer(self, *args, **kwargs):
        self.function_contents.trailer.append(self._print_to_string(*args, **kwargs))

    def _write_signal(self, declaration: VhdlDeclarationData) -> None:
        self.container.signals.append(VhdlSignal(instance=declaration.instance_name, 
        name=declaration.declaration_name, type=VhdlDeclarations(data_type=declaration.data_type)))

    def _flatten(self, xss: List[List[str]]) -> List[str]:
        return [x for xs in xss for x in xs]

    def _get_component_instantiation_generic_map(self, instance: VhdlInstanceData) -> str:
        if instance.generic_map is None:
            return ""
        generic_map = ", ".join(instance.generic_map)
        return f"""
generic map (
{generic_map}
)
        """

    def _get_component_instantiation_memory_port_map(self, instance: VhdlInstanceData) -> List[str]:
        vhdl_memory_port = VhdlMemoryPort()
        memory_port_map = []
        if instance.memory_interface is not None:
            master = instance.memory_interface.is_master()
            memory_port_map = vhdl_memory_port.get_port_map(name=instance.instance_name, master=master)
            self.container.instance_signals.add(vhdl_memory_port.get_port_signals(name=instance.instance_name))
        return memory_port_map
 
    def _get_input_port_map(self, input_port: VhdlInstructionArgument, instance: VhdlInstanceData) -> List[str]:
        vhdl_port = VhdlPortGenerator()
        memory_interface_name = instance.get_memory_port_name(port=input_port)
        if memory_interface_name is not None:
            vhdl_memory_port = VhdlMemoryPort()
            self.container.instance_signals.add(vhdl_memory_port.get_port_signals(name=memory_interface_name))
        return vhdl_port.get_port_map(
            input_port=input_port, memory_interface_name=memory_interface_name
        )

    def _get_input_port_maps(self, instance: VhdlInstanceData) -> List[str]:
        input_ports_map = [self._get_input_port_map(input_port=i, instance=instance) for i in instance.input_ports]
        return self._flatten(input_ports_map)

    def _get_component_instantiation_port_map(self, instance: VhdlInstanceData) -> str:
        vhdl_port = VhdlPortGenerator()
        input_ports_map = ["-- Input ports"] + self._get_input_port_maps(instance=instance)
        output_port_map = ["-- Output ports"] + vhdl_port.get_output_port_map(output_port=instance.output_port)
        memory_port_map = ["-- Memory ports"] + self._get_component_instantiation_memory_port_map(instance=instance)
        standard_port_map =  ["-- Standard port map"] + vhdl_port.get_standard_ports_map(instance=instance)
        tag_port_map = ["-- Tag port map"] + [f"s_tag => {self._local_tag_in}", f"m_tag => {self._local_tag_out}"]
        ports = input_ports_map + output_port_map + memory_port_map + standard_port_map + tag_port_map
        return ",\n".join(ports)
        
    def _write_component_instantiation(self, instance: VhdlInstanceData) -> None:
        instance_name = instance.instance_name
        entity_name = instance.entity_name
        generic_map = self._get_component_instantiation_generic_map(instance=instance)
        port_map = self._get_component_instantiation_port_map(instance=instance)
        source_line = instance.get_source_line()
        self._write_body(f"""
-- {source_line}
{instance_name}_inst : entity {instance.library}.{entity_name}
{generic_map}
port map (
{port_map}
);

        """)  

    def _write_component_output_signal_assignment(self, instance: VhdlInstanceData) -> None:
        self._write_body(f"""

process (all)
begin
  {instance.tag_name} <= conv_tag({self._local_tag_out});
  {instance.tag_name}.{instance.instance_name} <= m_tdata_i;
end process;

        """)
        
    def _write_instance_signals(self, instance: VhdlInstanceData) -> None:
        vhdl_port = VhdlPortGenerator()
        input_ports_signals = [vhdl_port.get_port_signal(input_port=i) for i in instance.input_ports]
        self._write_body(self._get_comment())
        self._write_body("signal tag_i : tag_t;")
        tag_signals = f"{self._local_tag_in}, {self._local_tag_out}"
        tag_type = "std_ulogic_vector(0 to c_tag_width - 1)"
        self._write_body(f"signal {tag_signals} : {tag_type};")
        for i in input_ports_signals:
            self._write_body(i)
        self._write_body(f"signal m_tdata_i : {instance.get_output_port_type()};")

    def _write_instance_signal_assignments(self, instance: VhdlInstanceData) -> None:
        vhdl_port = VhdlPortGenerator()
        input_ports_signal_assignment = [vhdl_port.get_port_signal_assignment(input_port=i, ports=self.container.ports, signals=self.container.signals) for i in instance.input_ports]
        tag_name = instance.get_previous_instance_signal_name("tag_out")
        self._write_body("tag_i <= " + ("tag_in_i" if tag_name is None else tag_name) + ";")
        self._write_body(f"{self._local_tag_in} <= tag_to_std_ulogic_vector(tag_i);")
        for i in input_ports_signal_assignment:
            self._write_body(i)
    
    def _write_instance(self, instance: VhdlInstanceData) -> None:
        if not instance.is_work_library():
            self.function_contents.instances.append(instance.entity_name)
        vhdl_port = VhdlPortGenerator()
        self.container.instance_signals.add(vhdl_port.get_standard_ports_signals(instance=instance))
        block_name = f"{instance.instance_name}_b"
        self._write_body(f"{block_name} : block")
        self._write_instance_signals(instance=instance)
        self._write_body("begin")
        self._write_instance_signal_assignments(instance=instance)
        self._write_component_instantiation(instance=instance)
        self._write_component_output_signal_assignment(instance=instance)
        self._write_body(f"end block {block_name};")
        
    def _write_instances(self, instances: VhdlInstanceContainerData, ports: PortContainer) -> None:
        self._write_body("tag_in_i.tag <= s_tag;")
        for i in ports.ports:
            if i.is_input():
                self._write_body(f"tag_in_i.{i.get_name()} <= {i.get_name()};")
        for j in instances.instances:
            self._write_instance(instance=j)
        return_driver = instances.get_return_instruction_driver()
        self._write_body(f"""
m_tvalid <= {return_driver}_m_tvalid_i;
{return_driver}_m_tready_i <= m_tready;
m_tdata <= conv_std_ulogic_vector(tag_out_i.{return_driver}, m_tdata'length);
m_tag <= tag_out_i.tag;
        """)
        
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
        self._write_body(assignments)
        
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
        self._write_body(f"""

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
        self._write_header(VhdlIncludeLibraries().get())
        
    def _write_architecture(self, function: VhdlFunctionDefinition) -> None:
        self._write_header(f"architecture rtl of {function.entity_name} is")
        self._write_declarations(declarations=function.declarations)
        self._write_instances(instances=function.instances, ports=function.ports)
        self._write_all_memory_arbiters(instances=function.instances, memory_port_names=function.get_memory_port_names())
        self._write_trailer("end architecture rtl;")

    def write_function(self, function: VhdlFunctionDefinition) -> FunctionContents:
        self.function_contents = FunctionContents()    
        self.container.ports = function.ports
        self._write_header(f"-- Autogenerated by {self._get_comment()}")
        self._write_include_libraries()
        self._write_header(VhdlEntity().get_entity(entity_name=function.entity_name, ports=function.ports))
        self._write_architecture(function=function)
        self._write_declarations_to_header()
        self._write_references_to_trailer()
        return self.function_contents

class FilePrinter:

    def generate(self, file_name: str, contents: List[FunctionContents]) -> None:
        with open(file_name, 'w', encoding="utf-8") as file_handle:
            for i in contents:
                print(i.get_contents(), file=file_handle, end="")
        base_name = os.path.splitext(file_name)[0]
        instance_file_name = f'{base_name}.inc'
        with open(instance_file_name, 'w', encoding="utf-8") as file_handle:
            for i in contents:
                print(i.get_instances(), file=file_handle)

