
from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import FrameType
from typing import List, Optional
from function_container_interface import FunctionContainerInterface
from function_contents_interface import FunctionContentsInterface
from instruction_argument import InstructionArgument
from language_generator import LanguageGeneratorCallData
from llvm_globals_container import GlobalsContainer
from llvm_type import LlvmVariableName
from llvm_type_declaration import TypeDeclaration
from vhdl_code_generator import VhdlCodeGenerator
from vhdl_declarations import VhdlDeclarations, VhdlSignal
from vhdl_instance_name import VhdlInstanceName
from vhdl_instruction import VhdlInstruction, VhdlInstructionContainer
from vhdl_instruction_argument import VhdlInstructionArgument, VhdlInstructionArgumentFactory
from vhdl_module import VhdlModule
from vhdl_port import VhdlMemoryPort, VhdlPortGenerator
from vhdl_signal_name import VhdlSignalName

class VhdlGeneratorInterface(ABC):
    @abstractmethod
    def generate_code(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        pass

    @abstractmethod
    def add_process_call(self, instruction: VhdlInstruction) -> None: 
        pass

    @abstractmethod
    def get_instance_name(self) -> str:
        pass

    @abstractmethod
    def get_tag_name(self) -> str:
        pass

    @abstractmethod
    def get_data_type(self) -> TypeDeclaration:
        pass

    def is_process(self) -> bool:
        return False
    
    def is_instance(self) -> bool:
        return False
    

class VhdlProcessGenerator(VhdlGeneratorInterface):
    calls: List[VhdlInstruction]

    def get_instance_name(self) -> str:
        raise NotImplementedError()

    def get_tag_name(self) -> str:
        raise NotImplementedError()

    def get_data_type(self) -> TypeDeclaration:
        raise NotImplementedError()

    def add_process_call(self, instruction: VhdlInstruction) -> None: 
        self.calls.append(instruction)

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
    instruction: VhdlInstruction
    instance_index: int
    entity_name: str
    instance_name: str
    previous_instance_name: Optional[str]
    
    _local_tag_in: str = "local_tag_in_i"
    _local_tag_out: str = "local_tag_out_i"   
   
    def get_data_type(self) -> TypeDeclaration:
        data_type = self.instruction.get_data_type()
        assert data_type is not None
        return data_type

    def get_instance_name(self) -> str:
        return self.instance_name

    def is_instance(self) -> bool:
        return True
    
    def _get_previous_instance_name(self) -> Optional[str]:
        return self.previous_instance_name

    def add_process_call(self, instruction: VhdlInstruction) -> None: 
        assert False, "add_process_callback should not be called"

    def _entity_name(self) -> str:
        return VhdlInstanceName(name=self.entity_name, library=self.instruction.get_library()).get_entity_name()

    def _is_work_library(self) -> bool:
        return self.instruction.is_work_library()

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
        memory_interface = self.instruction.get_memory_interface()
        if memory_interface is not None:
            master = memory_interface.is_master()
            memory_port_map = vhdl_memory_port.get_port_map(name=self.get_instance_name(), master=master)
            container.add_instance_signals(vhdl_memory_port.get_port_signals(name=self.get_instance_name()))
        return memory_port_map

    def _get_memory_port_name(self, port: VhdlInstructionArgument) -> Optional[str]:
        if not port.is_pointer():
            return None
        if not self.instruction.map_memory_interface():
            return None
        memory_interface_name = self.get_instance_name()
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
        standard_port_map =  ["-- Standard port map"] + vhdl_port.get_standard_ports_map(instance_name=self.get_instance_name(), 
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
        return self.instruction.get_source_line() 

    def _write_component_instantiation(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, 
                                       globals: GlobalsContainer) -> None:
        instance_name = self.get_instance_name()
        entity_name = self._entity_name()
        generic_map = self._get_component_instantiation_generic_map(generic_map=self.instruction.get_generic_map())
        port_map = self._get_component_instantiation_port_map(container=container, globals=globals)
        source_line = self._get_source_line()
        self._write_entity_instance(function_contents=function_contents, source_line=source_line, 
                                    instance_name=instance_name, library=self.instruction.get_library(), entity=entity_name, 
                                    generic_map=generic_map, port_map=port_map)

    def get_tag_name(self) -> str:
        tag_name = f"{self.get_instance_name()}_tag_out_i"
        return VhdlInstanceName(name=tag_name).get_entity_name()

    def _write_component_output_signal_assignment(self, function_contents: FunctionContentsInterface) -> None:
        comment = VhdlCodeGenerator().get_comment() 
        tag_name = self.get_tag_name()
        function_contents.write_body(f"""
{comment}
process (all)
begin
  {tag_name} <= conv_tag({self._local_tag_out});
  {tag_name}.{self.get_instance_name()} <= m_tdata_i;
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
        return [VhdlInstructionArgumentFactory().get(instruction_argument=i, globals=globals) for i in self.instruction.get_operands()]
        
    def _get_output_port_type(self) -> str:
        assert self.data.output_port is not None, \
            f"Instance {self.get_instance_name()} output port is not defined"
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
        container.add_instance_signals(vhdl_port.get_standard_ports_signals(instance_name=self.get_instance_name()))
        block_name = f"{self.get_instance_name()}_b"
        function_contents.write_body(f"{block_name} : block")
        self._write_instance_signals(function_contents=function_contents, globals=globals)
        self._write_instance_contents(block_name=block_name, function_contents=function_contents, container=container, globals=globals)

@dataclass
class VhdlReturnGenerator(VhdlGeneratorInterface):
    data_type: TypeDeclaration
    operands: List[InstructionArgument]

    def add_process_call(self, data: LanguageGeneratorCallData) -> None: 
        raise NotImplementedError()

    def get_instance_name(self) -> str:
        raise NotImplementedError()

    def get_tag_name(self) -> str:
        raise NotImplementedError()

    def get_data_type(self) -> TypeDeclaration:
        raise NotImplementedError()

    def generate_code(self, function_contents: FunctionContentsInterface, container: FunctionContainerInterface, globals: GlobalsContainer) -> None:
        pass
    
class VhdlGenerator:
    
    _generators: List[VhdlGeneratorInterface]
    _instance_index: int
    _previous_instance: Optional[VhdlInstanceGenerator]

    def __init__(self):
        self._generators = []
        self._instance_index = 1
        self._previous_instance = None

    def write_instance(self, instance):
        pass
    
    def write_signal_declaration(self, name: Optional[LlvmVariableName], data_type: TypeDeclaration) -> None:
        pass    

    def _get_previous_instance_name(self) -> Optional[str]:
        if self._previous_instance is None:
            return None
        return self._previous_instance.instance_name

    def add_instruction(self, instruction: VhdlInstruction) -> None:
        entity_name = instruction.get_name()
        instance_name = f"{entity_name}_{self._instance_index}"
        instance = VhdlInstanceGenerator(instruction=instruction, instance_index=self._instance_index, entity_name=entity_name, 
                                        instance_name=instance_name, previous_instance_name=self._get_previous_instance_name())
        self._generators.append(instance)
        self._instance_index += 1
        self._previous_instance = instance

    def _get_last_process(self) -> VhdlGeneratorInterface:
        if len(self._generators) == 0 or not self._generators[-1].is_process():
            return VhdlProcessGenerator()
        return self._generators[-1]
    
    def process_call(self, data: LanguageGeneratorCallData) -> None:
        process = self._get_last_process()
        process.add_process_call(data=data)

    def return_operation(self, data_type: TypeDeclaration, operands: List[InstructionArgument]) -> None:
        pass

    def _write_return(self, function_contents: FunctionContentsInterface) -> None:
        return_driver = self._get_previous_instance_name()
        assert self._previous_instance is not None, "No instance was created"
        previous_instance_tag_name = self._previous_instance.get_tag_name()
        function_contents.write_body(f"""
tag_out_i <= {previous_instance_tag_name};
m_tvalid <= {return_driver}_m_tvalid_i;
{return_driver}_m_tready_i <= m_tready;
m_tdata <= conv_std_ulogic_vector(tag_out_i.{return_driver}, m_tdata'length);
m_tag <= tag_out_i.tag;
        """)

    def _write_signal(self, container: FunctionContainerInterface, generator: VhdlGeneratorInterface) -> None:
        container.add_signal(VhdlSignal(instance=generator.get_instance_name(), 
        name=generator.get_tag_name(), type=VhdlDeclarations(data_type=generator.get_data_type())))

    def _write_instance_signals(self, container: FunctionContainerInterface) -> None:
        for i in self._generators:
            if i.is_instance():
                self._write_signal(container=container, generator=i)

    def generate_code(self, instructions: VhdlInstructionContainer, external_pointer_names: List[str], 
                      function_contents: FunctionContentsInterface, container: FunctionContainerInterface, 
                      module: VhdlModule) -> None:
        self._write_instance_signals(container=container)
        for instruction in instructions.instructions:
            if instruction.access_register(external_pointer_names=external_pointer_names):
                self.add_process_call(instruction=instruction)
            else:
                self.add_instruction(instrucction=instruction)
        for generator in self._generators:
            generator.generate_code(function_contents=function_contents, container=container, globals=module.module.globals)
        self._write_return(function_contents=function_contents)