
import inspect
import os
from types import FrameType
from typing import Optional

from frame_info import FrameInfoFactory
from llvm_type import LlvmVariableName

class VhdlCodeGenerator:
    
    def get_vhdl_name(self, llvm_name: str) -> str:
        return llvm_name.replace("@", "").strip("_").replace("__", "_")

    def get_variable_name(self, name: str) -> str:
        return f"{name}_v"

    def translate_variable_name(self, name: str) -> str:
        return f"var_{name}"

    def get_destination_variable_name(self, name: LlvmVariableName) -> str:
        return self.translate_variable_name(name = name.translate_name())
    
    def get_signal_name(self, name: str) -> str:
        return f"{name}_i"

    def _get_declaration(self, declaration_type: str, name: str, data_width: str) -> str:
        return f"{declaration_type} {name} : std_ulogic_vector({data_width} - 1 downto 0);"

    def get_variable_declaration(self, name: str, data_width: str) -> str:
        name = self.get_variable_name(name)
        return self._get_declaration(declaration_type="variable", name=name, data_width=data_width)

    def get_signal_declaration(self, name: str, data_width: str) -> str:
        name = self.get_variable_name(name)
        return self._get_declaration(declaration_type="signal", name=name, data_width=data_width)

    def get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        if current_frame is None:
            current_frame = inspect.currentframe()
        frame_info = FrameInfoFactory().get_frame_info(current_frame=current_frame)
        assert frame_info.file_name is not None
        file_name = os.path.basename(frame_info.file_name)
        return f"-- {file_name}({frame_info.line_number}): "


