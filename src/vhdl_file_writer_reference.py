
from dataclasses import dataclass
from typing import List, Optional

from llvm_constant import DeclarationBase
from llvm_function import LlvmFunction, LlvmFunctionContainer
from ports import PortContainer
from vhdl_code_generator import VhdlCodeGenerator
from vhdl_entity import VhdlEntity
from vhdl_include_libraries import VhdlIncludeLibraries


@dataclass
class VhdlFileWriterReference:
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
        comment = VhdlCodeGenerator().get_comment()
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
