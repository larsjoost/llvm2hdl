


from dataclasses import dataclass, field
import inspect
from typing import List, Optional
from vhdl_comment_generator import VhdlCommentGenerator
from llvm_constant import DeclarationBase
from llvm_function import LlvmFunction, LlvmFunctionContainer
from ports import PortContainer

from vhdl_declarations import VhdlDeclarations, VhdlSignal
from vhdl_entity import VhdlEntity
from vhdl_include_libraries import VhdlIncludeLibraries

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
        comment = VhdlCommentGenerator().get_comment()
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
        comment = VhdlCommentGenerator().get_comment() 
        name = self.variable.get_name()
        data_width = self.variable.get_data_width()
        return f"""
{comment} Global variables
signal {name} : std_ulogic_vector(0 to {data_width} - 1);
        """

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
        comment = VhdlCommentGenerator().get_comment(current_frame=inspect.currentframe())
        self.signals.append(Signals(comment=comment, signals=signals))

@dataclass
class VhdlFunctionContainer:
    signals : List[VhdlSignal] = field(default_factory=list)
    instance_signals: InstanceSignals = field(default_factory=lambda : InstanceSignals())
    constants : List[FileWriterConstant] = field(default_factory=list)
    references: List[FileWriterReference] = field(default_factory=list)
    variables: List[FileWriterVariable] = field(default_factory=list)
    ports: PortContainer = field(default_factory=lambda : PortContainer())
