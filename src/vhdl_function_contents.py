
from dataclasses import dataclass, field
import inspect
import io
from types import FrameType
from typing import List, Optional

from vhdl_comment_generator import VhdlCommentGenerator


@dataclass
class VhdlFunctionContents:
    header : List[str] =  field(default_factory=list) 
    body : List[str]  =  field(default_factory=list)
    trailer : List[str]  =  field(default_factory=list)
    instances : List[str]  =  field(default_factory=list)
    
    def _get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        return VhdlCommentGenerator().get_comment(current_frame=current_frame)
        
    def _print_to_string(self, *args, **kwargs) -> str:
        with io.StringIO() as output:
            print(*args, file=output, **kwargs)
            contents = output.getvalue()
        return contents
    
    def _append(self, contents: List[str], current_frame: Optional[FrameType], content: str) -> None:
        comment = self._get_comment(current_frame=current_frame)
        contents.append(f"{comment}\n{content}")

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
