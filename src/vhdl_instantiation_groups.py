
from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import FrameType
from typing import List, Optional
from vhdl_comment_generator import VhdlCommentGenerator
from vhdl_function_container import VhdlFunctionContainer
from vhdl_function_contents import VhdlFunctionContents

from vhdl_instance_data import VhdlInstanceData
from vhdl_instruction_argument import VhdlInstructionArgument
from vhdl_port import VhdlMemoryPort, VhdlPortGenerator

class VhdlInstantiationGroupBase(ABC):
    @abstractmethod
    def append(self, instance: VhdlInstanceData) -> bool:
        pass
    @abstractmethod
    def write_instances(self, function_contents: VhdlFunctionContents, container: VhdlFunctionContainer) -> None:
        pass

@dataclass
class VhdlRegisterAccessGroup(VhdlInstantiationGroupBase):
    instances: List[VhdlInstanceData]
    def append(self, instance: VhdlInstanceData) -> bool:
        if not instance.access_register():
            return False
        self.instances.append(instance)
        return True
    def write_instances(self, function_contents: VhdlFunctionContents, container: VhdlFunctionContainer) -> None:
        pass
 
pass

@dataclass    
class VhdlInstanceGroup(VhdlInstantiationGroupBase):
    instance: VhdlInstanceData

    _local_tag_in: str = "local_tag_in_i"
    _local_tag_out: str = "local_tag_out_i"   
   
    def append(self, instance: VhdlInstanceData) -> bool:
        return False
    
    def _get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        return VhdlCommentGenerator().get_comment(current_frame=current_frame)        

    def _write_input_port_signal_assignments(self, instance: VhdlInstanceData, function_contents: VhdlFunctionContents, container: VhdlFunctionContainer) -> None:
        vhdl_port = VhdlPortGenerator()
        input_ports_signal_assignment = [vhdl_port.get_port_signal_assignment(input_port=i, ports=container.ports, signals=container.signals) for i in instance.input_ports]
        for i in input_ports_signal_assignment:
            function_contents.write_body(i)
                
    def _write_instance_signal_assignments(self, instance: VhdlInstanceData, function_contents: VhdlFunctionContents, container: VhdlFunctionContainer) -> None:
        tag_name = instance.get_previous_instance_signal_name("tag_out")
        function_contents.write_body("tag_i <= " + ("tag_in_i" if tag_name is None else tag_name) + ";")
        function_contents.write_body(f"{self._local_tag_in} <= tag_to_std_ulogic_vector(tag_i);")
        self._write_input_port_signal_assignments(instance=instance, function_contents=function_contents, container=container)

    def _write_entity_instance(self, function_contents: VhdlFunctionContents, source_line: str, 
                               instance_name: str, library: str, entity: str, generic_map: str, port_map: str) -> None:
        function_contents.write_body(f"""
-- {source_line}
{instance_name}_inst : entity {library}.{entity}
{generic_map}
port map (
{port_map}
);

        """)  

    def _get_component_instantiation_memory_port_map(self, instance: VhdlInstanceData, container: VhdlFunctionContainer) -> List[str]:
        vhdl_memory_port = VhdlMemoryPort()
        memory_port_map = []
        if instance.memory_interface is not None:
            master = instance.memory_interface.is_master()
            memory_port_map = vhdl_memory_port.get_port_map(name=instance.instance_name, master=master)
            container.instance_signals.add(vhdl_memory_port.get_port_signals(name=instance.instance_name))
        return memory_port_map

    def _get_input_port_map(self, input_port: VhdlInstructionArgument, instance: VhdlInstanceData, container: VhdlFunctionContainer) -> List[str]:
        vhdl_port = VhdlPortGenerator()
        memory_interface_name = instance.get_memory_port_name(port=input_port)
        if memory_interface_name is not None:
            vhdl_memory_port = VhdlMemoryPort()
            container.instance_signals.add(vhdl_memory_port.get_port_signals(name=memory_interface_name))
        return vhdl_port.get_port_map(
            input_port=input_port, memory_interface_name=memory_interface_name
        )

    def _flatten(self, xss: List[List[str]]) -> List[str]:
        return [x for xs in xss for x in xs]

    def _get_input_port_maps(self, instance: VhdlInstanceData, container: VhdlFunctionContainer) -> List[str]:
        input_ports_map = [self._get_input_port_map(input_port=i, instance=instance, container=container) for i in instance.input_ports]
        return self._flatten(input_ports_map)
 
    def _get_component_instantiation_port_map(self, instance: VhdlInstanceData, container: VhdlFunctionContainer) -> str:
        vhdl_port = VhdlPortGenerator()
        input_ports_map = ["-- Input ports"] + self._get_input_port_maps(instance=instance, container=container)
        output_port_map = ["-- Output ports"] + vhdl_port.get_output_port_map(output_port=instance.output_port)
        memory_port_map = ["-- Memory ports"] + self._get_component_instantiation_memory_port_map(instance=instance, container=container)
        standard_port_map =  ["-- Standard port map"] + vhdl_port.get_standard_ports_map(instance=instance)
        tag_port_map = ["-- Tag port map"] + [f"s_tag => {self._local_tag_in}", f"m_tag => {self._local_tag_out}"]
        ports = input_ports_map + output_port_map + memory_port_map + standard_port_map + tag_port_map
        return ",\n".join(ports)

    def _get_component_instantiation_generic_map(self, instance: VhdlInstanceData) -> str:
        if instance.generic_map is None:
            return ""
        generic_map = ", ".join(instance.generic_map)
        return f"""
generic map (
{generic_map}
)
        """

 
    def _write_component_instantiation(self, instance: VhdlInstanceData, function_contents: VhdlFunctionContents, container: VhdlFunctionContainer) -> None:
        instance_name = instance.instance_name
        entity_name = instance.entity_name
        generic_map = self._get_component_instantiation_generic_map(instance=instance)
        port_map = self._get_component_instantiation_port_map(instance=instance, container=container)
        source_line = instance.get_source_line()
        self._write_entity_instance(function_contents=function_contents, source_line=source_line, 
                                    instance_name=instance_name, library=instance.library, entity=entity_name, 
                                    generic_map=generic_map, port_map=port_map)

    def _write_component_output_signal_assignment(self, instance: VhdlInstanceData, function_contents: VhdlFunctionContents) -> None:
        comment = VhdlCommentGenerator().get_comment() 
        function_contents.write_body(f"""
{comment}
process (all)
begin
  {instance.tag_name} <= conv_tag({self._local_tag_out});
  {instance.tag_name}.{instance.instance_name} <= m_tdata_i;
end process;

        """)

    def _write_instance_contents(self, block_name: str, instance: VhdlInstanceData, function_contents: VhdlFunctionContents, container: VhdlFunctionContainer) -> None:
        function_contents.write_body("begin")
        self._write_instance_signal_assignments(instance=instance, function_contents=function_contents, container=container)
        self._write_component_instantiation(instance=instance, function_contents=function_contents, container=container)
        self._write_component_output_signal_assignment(instance=instance, function_contents=function_contents)
        function_contents.write_body(f"end block {block_name};")
 
    def _write_instance_signals(self, instance: VhdlInstanceData, function_contents: VhdlFunctionContents) -> None:
        vhdl_port = VhdlPortGenerator()
        input_ports_signals = [vhdl_port.get_port_signal(input_port=i) for i in instance.input_ports]
        function_contents.write_body(self._get_comment())
        function_contents.write_body("signal tag_i : tag_t;")
        tag_signals = f"{self._local_tag_in}, {self._local_tag_out}"
        tag_type = "std_ulogic_vector(0 to c_tag_width - 1)"
        function_contents.write_body(f"signal {tag_signals} : {tag_type};")
        for i in input_ports_signals:
            function_contents.write_body(i)
        function_contents.write_body(f"signal m_tdata_i : {instance.get_output_port_type()};")

    def write_instances(self, function_contents: VhdlFunctionContents, container: VhdlFunctionContainer) -> None:
        if not self.instance.is_work_library():
            function_contents.append_instance(self.instance.entity_name)
        vhdl_port = VhdlPortGenerator()
        container.instance_signals.add(vhdl_port.get_standard_ports_signals(instance=self.instance))
        block_name = f"{self.instance.instance_name}_b"
        function_contents.write_body(f"{block_name} : block")
        self._write_instance_signals(instance=self.instance, function_contents=function_contents)
        self._write_instance_contents(block_name=block_name, instance=self.instance, function_contents=function_contents, container=container)

class VhdlInstantiationGroupsGenerator:

    def _add_group(self, groups: List[VhdlInstantiationGroupBase], instance: VhdlInstanceData) -> None:
        if instance.access_register():
            groups.append(VhdlRegisterAccessGroup(instances=[instance]))
        else:
            groups.append(VhdlInstanceGroup(instance=instance))

    def get_groups(self, instances: List[VhdlInstanceData]) -> List[VhdlInstantiationGroupBase]:
        groups: List[VhdlInstantiationGroupBase] = []
        for i in instances:
            appended_to_group = groups[-1].append(instance=i) if groups else False
            if not appended_to_group:
                self._add_group(groups=groups, instance=i)
        return groups

class VhdlInstantiationGroupWriter:

    def write_instances(self, instances: List[VhdlInstanceData], function_contents: VhdlFunctionContents, container: VhdlFunctionContainer) -> None:
        groups = VhdlInstantiationGroupsGenerator().get_groups(instances=instances)
        for instances_group in groups:
            instances_group.write_instances(function_contents=function_contents, container=container)
