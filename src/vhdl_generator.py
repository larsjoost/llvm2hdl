
from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import FrameType
from typing import List, Optional
from function_container_interface import FunctionContainerInterface
from function_contents_interface import FunctionContentsInterface
from instruction_argument import InstructionArgument
from language_generator import LanguageGenerator, LanguageGeneratorCallData, LanguageGeneratorInstanceData
from llvm_globals_container import GlobalsContainer
from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration
from vhdl_code_generator import VhdlCodeGenerator
from vhdl_function_contents import VhdlFunctionContents
from vhdl_instance_name import VhdlInstanceName
from vhdl_instruction_argument import VhdlInstructionArgument, VhdlInstructionArgumentFactory
from vhdl_port import VhdlMemoryPort, VhdlPortGenerator
from vhdl_signal_name import VhdlSignalName

class VhdlGeneratorInterface(ABC):
    @abstractmethod
    def generate_code(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        pass

    @abstractmethod
    def add_process_call(self, data: LanguageGeneratorCallData) -> None: 
        pass

    def is_process(self) -> bool:
        return False
    

class VhdlProcessGenerator(VhdlGeneratorInterface):
    calls: List[LanguageGeneratorCallData]
    def add_process_call(self, data: LanguageGeneratorCallData) -> None: 
        self.calls.append(data)
    def is_process(self) -> bool:
        return True
    def _get_input_arguments(self, call: LanguageGeneratorCallData, globals: GlobalsContainer) -> List[str]:
        return [VhdlInstructionArgumentFactory().get(instruction_argument=i, globals=globals).signal_name for i in call.operands]
    def _get_function_call(self, call: LanguageGeneratorCallData, globals: GlobalsContainer) -> str:
        arguments = ", ".join(self._get_input_arguments(call=call, globals=globals))
        return f"{call.opcode}({arguments})"
    def _get_instance_calls(self, globals: GlobalsContainer) -> List[str]:
        return [self._get_function_call(call=i, globals=globals) for i in self.calls]
    def _get_variables(self) -> List[str]:
        variables = []
        for i in self.calls:
            variables.extend(i.get_variable_declarations())
        return variables
    def generate_code(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        variables = self._get_variables()
        declaration = "\n".join(variables)
        instance_calls = self._get_instance_calls(globals=globals)
        body = "\n".join(instance_calls)
        function_contents.write_body(f"""
process (clk)
{declaration}
begin
{body}
end process;
        """)

@dataclass    
class VhdlInstanceGenerator(VhdlGeneratorInterface):
    data: LanguageGeneratorInstanceData
    instance_index: int
    entity_name: str
    instance_name: str
    previous_instance_name: Optional[str]
    
    _local_tag_in: str = "local_tag_in_i"
    _local_tag_out: str = "local_tag_out_i"   
   
    def _get_instance_name(self) -> str:
        return self.instance_name

    def _get_previous_instance_name(self) -> Optional[str]:
        return self.previous_instance_name

    def add_process_call(self, data: LanguageGeneratorCallData) -> None: 
        assert False, "add_process_callback should not be called"

    def _entity_name(self) -> str:
        return VhdlInstanceName(name=self.entity_name, library=self.data.library).get_entity_name()

    def _is_work_library(self) -> bool:
        return self.data.library == "work"

    def _get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        return VhdlCodeGenerator().get_comment(current_frame=current_frame)        

    def _write_input_port_signal_assignments(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        vhdl_port = VhdlPortGenerator()
        input_ports_signal_assignment = [vhdl_port.get_port_signal_assignment(input_port=i, ports=container.get_ports(), signals=container.get_signals()) for i in self._input_ports(globals=globals)]
        for i in input_ports_signal_assignment:
            function_contents.write_body(i)

    def _get_previous_instance_signal_name(self, signal_name: str) -> Optional[str]:
        name = self._get_previous_instance_name()
        if name is None:
            return None
        return VhdlSignalName(instance_name=name, signal_name=signal_name).get_signal_name()
    
    def _write_instance_signal_assignments(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        tag_name = self._get_previous_instance_signal_name("tag_out")
        function_contents.write_body("tag_i <= " + ("tag_in_i" if tag_name is None else tag_name) + ";")
        function_contents.write_body(f"{self._local_tag_in} <= tag_to_std_ulogic_vector(tag_i);")
        self._write_input_port_signal_assignments(function_contents=function_contents, container=container, globals=globals)

    def _write_entity_instance(self, function_contents: FunctionContentsInterface, source_line: str, 
                               instance_name: str, library: str, entity: str, generic_map: str, port_map: str) -> None:
        function_contents.write_body(f"""
-- {source_line}
{instance_name}_inst : entity {library}.{entity}
{generic_map}
port map (
{port_map}
);

        """)  

    def _get_component_instantiation_memory_port_map(self, container: FunctionContainerInterface) -> List[str]:
        vhdl_memory_port = VhdlMemoryPort()
        memory_port_map = []
        if self.data.memory_interface is not None:
            master = self.data.memory_interface.is_master()
            memory_port_map = vhdl_memory_port.get_port_map(name=self._get_instance_name(), master=master)
            container.add_instance_signals(vhdl_memory_port.get_port_signals(name=self._get_instance_name()))
        return memory_port_map

    def _get_memory_port_name(self, port: VhdlInstructionArgument) -> Optional[str]:
        if not port.is_pointer():
            return None
        if not self.data.map_memory_interface:
            return None
        memory_interface_name = self._get_instance_name()
        return f"{memory_interface_name}_{port.get_name()}"

    def _get_input_port_map(self, input_port: VhdlInstructionArgument, container: FunctionContainerInterface) -> List[str]:
        vhdl_port = VhdlPortGenerator()
        memory_interface_name = self._get_memory_port_name(port=input_port)
        if memory_interface_name is not None:
            vhdl_memory_port = VhdlMemoryPort()
            container.add_instance_signals(vhdl_memory_port.get_port_signals(name=memory_interface_name))
        return vhdl_port.get_port_map(
            input_port=input_port, memory_interface_name=memory_interface_name
        )

    def _flatten(self, xss: List[List[str]]) -> List[str]:
        return [x for xs in xss for x in xs]

    def _get_input_port_maps(self, container: FunctionContainerInterface, globals: GlobalsContainer) -> List[str]:
        input_ports_map = [self._get_input_port_map(input_port=i, container=container) for i in self._input_ports(globals=globals)]
        return self._flatten(input_ports_map)
 
    def _get_component_instantiation_port_map(self, container: FunctionContainerInterface, globals: GlobalsContainer) -> str:
        vhdl_port = VhdlPortGenerator()
        input_ports_map = ["-- Input ports"] + self._get_input_port_maps(container=container, globals=globals)
        output_port_map = ["-- Output ports"] + vhdl_port.get_output_port_map(output_port=self.data.output_port)
        memory_port_map = ["-- Memory ports"] + self._get_component_instantiation_memory_port_map(container=container)
        standard_port_map =  ["-- Standard port map"] + vhdl_port.get_standard_ports_map(instance_name=self._get_instance_name(), 
                                                                                         previous_instance_name=self._get_previous_instance_name())
        tag_port_map = ["-- Tag port map"] + [f"s_tag => {self._local_tag_in}", f"m_tag => {self._local_tag_out}"]
        ports = input_ports_map + output_port_map + memory_port_map + standard_port_map + tag_port_map
        return ",\n".join(ports)

    def _get_component_instantiation_generic_map(self, generic_map: Optional[List[str]]) -> str:
        if generic_map is None:
            return ""
        mapping = ", ".join(generic_map)
        return f"""
generic map (
{mapping}
)
        """
 
    def _get_source_line(self) -> str:
        return self.data.source_line.get_elaborated()        

    def _write_component_instantiation(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, 
                                       globals: GlobalsContainer) -> None:
        instance_name = self._get_instance_name()
        entity_name = self._entity_name()
        generic_map = self._get_component_instantiation_generic_map(generic_map=self.data.generic_map)
        port_map = self._get_component_instantiation_port_map(container=container, globals=globals)
        source_line = self._get_source_line()
        self._write_entity_instance(function_contents=function_contents, source_line=source_line, 
                                    instance_name=instance_name, library=self.data.library, entity=entity_name, 
                                    generic_map=generic_map, port_map=port_map)

    def _get_tag_name(self) -> str:
        tag_name = f"{self._get_instance_name()}_tag_out_i"
        return VhdlInstanceName(name=tag_name).get_entity_name()

    def _write_component_output_signal_assignment(self, function_contents: FunctionContentsInterface) -> None:
        comment = VhdlCodeGenerator().get_comment() 
        tag_name = self._get_tag_name()
        function_contents.write_body(f"""
{comment}
process (all)
begin
  {tag_name} <= conv_tag({self._local_tag_out});
  {tag_name}.{self._get_instance_name()} <= m_tdata_i;
end process;

        """)

    def _write_instance_contents(self, block_name: str, function_contents: FunctionContentsInterface, 
                                 container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        function_contents.write_body("begin")
        self._write_instance_signal_assignments(function_contents=function_contents, container=container, globals=globals)
        self._write_component_instantiation(function_contents=function_contents, container=container, globals=globals)
        self._write_component_output_signal_assignment(function_contents=function_contents)
        function_contents.write_body(f"end block {block_name};")
 
    def _input_ports(self, globals: GlobalsContainer) -> List[VhdlInstructionArgument]:
        return [VhdlInstructionArgumentFactory().get(instruction_argument=i, globals=globals) for i in self.data.operands]
        
    def _get_output_port_type(self) -> str:
        assert self.data.output_port is not None, \
            f"Instance {self._get_instance_name()} output port is not defined"
        return self.data.output_port.get_type_declarations()

    def _write_instance_signals(self, function_contents: FunctionContentsInterface, globals: GlobalsContainer) -> None:
        vhdl_port = VhdlPortGenerator()
        input_ports_signals = [vhdl_port.get_port_signal(input_port=i) for i in self._input_ports(globals=globals)]
        function_contents.write_body(self._get_comment())
        function_contents.write_body("signal tag_i : tag_t;")
        tag_signals = f"{self._local_tag_in}, {self._local_tag_out}"
        tag_type = "std_ulogic_vector(0 to c_tag_width - 1)"
        function_contents.write_body(f"signal {tag_signals} : {tag_type};")
        for i in input_ports_signals:
            function_contents.write_body(i)
        function_contents.write_body(f"signal m_tdata_i : {self._get_output_port_type()};")

    def generate_code(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        if not self._is_work_library():
            function_contents.append_instance(self._entity_name())
        vhdl_port = VhdlPortGenerator()
        container.add_instance_signals(vhdl_port.get_standard_ports_signals(instance_name=self._get_instance_name()))
        block_name = f"{self._get_instance_name()}_b"
        function_contents.write_body(f"{block_name} : block")
        self._write_instance_signals(function_contents=function_contents, globals=globals)
        self._write_instance_contents(block_name=block_name, function_contents=function_contents, container=container, globals=globals)

@dataclass
class VhdlReturnGenerator(VhdlGeneratorInterface):
    data_type: TypeDeclaration
    operands: List[InstructionArgument]

    def add_process_call(self, data: LanguageGeneratorCallData) -> None: 
        assert False, "add_process_callback should not be called"

    def generate_code(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        pass
    
class VhdlGenerator(LanguageGenerator):
    
    _contents: VhdlFunctionContents
    _generators: List[VhdlGeneratorInterface]
    _instance_index: int
    _previous_instance_name: Optional[str]

    def __init__(self, contents: VhdlFunctionContents):
        self._contents = contents
        self._generators = []
        self._instance_index = 1
        self._previous_instance_name = None

    def write_instance(self, instance):
        pass
    
    def write_signal_declaration(self, name: Optional[LlvmVariableName], data_type: TypeDeclaration) -> None:
        pass    

    def instance(self, data: LanguageGeneratorInstanceData, opcode_name: str) -> None:
        entity_name = VhdlCodeGenerator().get_vhdl_name(llvm_name=opcode_name)
        instance_name = f"{entity_name}_{self._instance_index}"
        self._generators.append(VhdlInstanceGenerator(data=data, instance_index=self._instance_index, entity_name=entity_name, 
                                                      instance_name=instance_name, previous_instance_name=self._previous_instance_name))
        self._instance_index += 1
        self._previous_instance_name = instance_name

    def _get_last_process(self) -> VhdlGeneratorInterface:
        if len(self._generators) == 0 or not self._generators[-1].is_process():
            return VhdlProcessGenerator()
        return self._generators[-1]
    
    def process_call(self, data: LanguageGeneratorCallData) -> None:
        process = self._get_last_process()
        process.add_process_call(data=data)

    def write_body(self, text: str) -> None:
        self._contents.write_body(text)

    def return_operation(self, data_type: TypeDeclaration, operands: List[InstructionArgument]) -> None:
        pass

    def generate_code(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        for generator in self._generators:
            generator.generate_code(function_contents=function_contents, container=container, globals=globals)