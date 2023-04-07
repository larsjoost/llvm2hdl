
from dataclasses import dataclass, field
import inspect
import io
from types import FrameType
from typing import List, Optional
from function_contents_interface import FunctionContentsInterface

from vhdl_code_generator import VhdlCodeGenerator


@dataclass
class VhdlFunctionContents(FunctionContentsInterface):
    name: str
    header : List[str] =  field(default_factory=list) 
    declaration : List[str]  =  field(default_factory=list)
    body : List[str]  =  field(default_factory=list)
    trailer : List[str]  =  field(default_factory=list)
    instances : List[str]  =  field(default_factory=list)
    
    def _get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        return VhdlCodeGenerator().get_comment(current_frame=current_frame)
        
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

begin

{self.get_description("Body")} 

{self._to_string(self.body)}  
        
{self.get_description("Trailer")} 

{self._to_string(self.trailer)}

end architecture rtl;
        """
    def get_instances(self) -> str:
        return "\n".join(self.instances)
    def ___str__(self) -> str:
        return self.get_contents()
    def __repr__(self) -> str:
        return self.get_contents()
