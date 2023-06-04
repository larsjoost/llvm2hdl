
from dataclasses import dataclass, field
import inspect
import io
from types import FrameType
from typing import List, Optional
from function_contents_interface import FunctionContentsInterface
from llvm_type_declaration import TypeDeclaration
from ports import PortContainer
from signal_interface import SignalInterface
from vhdl_code_generator import VhdlCodeGenerator
from vhdl_declarations import VhdlDeclarations, VhdlTagSignal
from vhdl_function_container import VhdlFileWriterVariable, VhdlFunctionContainer
from vhdl_file_writer_reference import VhdlFileWriterReference

@dataclass
class VhdlFunctionContents(FunctionContentsInterface):
    name: str
    header : List[str] =  field(default_factory=list) 
    declaration : List[str]  =  field(default_factory=list)
    signal_declaration : List[str]  =  field(default_factory=list)
    body : List[str]  =  field(default_factory=list)
    trailer : List[str]  =  field(default_factory=list)
    instances : List[str]  =  field(default_factory=list)
    container: VhdlFunctionContainer = field(default_factory=VhdlFunctionContainer)

    def _get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        return VhdlCodeGenerator().get_comment(current_frame=current_frame)
        
    def get_comment(self, contents: str) -> str:
        return f"{self._get_comment(current_frame=inspect.currentframe())} {contents}"

    def get_signals(self) -> List[SignalInterface]:
        return self.container.get_signals()

    def add_signal(self, signal: SignalInterface) -> None:
        self.container.add_signal(signal)

    def get_instance_signals(self) -> str:
        return self.container.instance_signals.get_signals()

    def add_instance_signals(self, signals: List[str]) -> None:
        self.container.add_instance_signals(signals=signals)

    def get_ports(self) -> PortContainer:
        return self.container.get_ports()

    def get_variables(self) -> List[VhdlFileWriterVariable]:
        return self.container.variables

    def add_variable(self, variable: VhdlFileWriterVariable) -> None:
        self.container.variables.append(variable)

    def get_references(self) -> List[VhdlFileWriterReference]:
        return self.container.references
    
    def add_reference(self, reference: VhdlFileWriterReference) -> None:
        self.container.references.append(reference)

    def _print_to_string(self, *args, **kwargs) -> str:
        with io.StringIO() as output:
            print(*args, file=output, **kwargs)
            contents = output.getvalue()
        return contents

    def _append(self, contents: List[str], current_frame: Optional[FrameType], content: str) -> None:
        comment = self._get_comment(current_frame=current_frame)
        contents.append(f"{comment}\n{content}")

    def write_declaration(self, *args, **kwargs) -> None:
        content = self._print_to_string(*args, **kwargs)
        self._append(contents=self.declaration, current_frame=inspect.currentframe(), content=content)

    def write_tag_declaration(self, signal_name: str, instance_name: str, destination: Optional[str], data_type: TypeDeclaration) -> None:
        signal = VhdlTagSignal(instance=destination, name=signal_name, type=VhdlDeclarations(data_type))
        self._append(contents=self.signal_declaration, current_frame=inspect.currentframe(), content=signal.get_signal_declaration())
        if destination is not None:
            self.add_signal(signal=signal) 

    def write_body(self, *args, **kwargs) -> None:
        content = self._print_to_string(*args, **kwargs)
        self._append(contents=self.body, current_frame=inspect.currentframe(), content=content)

    def write_header(self, *args, **kwargs) -> None:
        content = self._print_to_string(*args, **kwargs)
        self._append(contents=self.header, current_frame=inspect.currentframe(), content=content)

    def write_trailer(self, *args, **kwargs) -> None:
        content = self._print_to_string(*args, **kwargs)
        self._append(contents=self.trailer, current_frame=inspect.currentframe(), content=content)

    def append_instance(self, name: str) -> None:
        self.instances.append(name)

    def _to_string(self, data: List[str]) -> str:
        return "\n".join(data)

    def get_description(self, text: str) -> str:
        return f"""
--------------------------------------------------------------------------------
-- {text}
--------------------------------------------------------------------------------
        """

    def get_contents(self) -> str:
        return f"""
        
{self.get_description("Header")} 

{self._to_string(self.header)} 
        
architecture rtl of {self.name} is

{self.get_description("Declaration")} 

{self._to_string(self.declaration)}  

{self.get_description("Signal Declaration")} 

{self._to_string(self.signal_declaration)}  

begin

{self.get_description("Body")} 

{self._to_string(self.body)}  
        
end architecture rtl;

{self.get_description("Trailer")} 

{self._to_string(self.trailer)}

        """
    def get_instances(self) -> str:
        return "\n".join(self.instances)
    def ___str__(self) -> str:
        return self.get_contents()
    def __repr__(self) -> str:
        return self.get_contents()
