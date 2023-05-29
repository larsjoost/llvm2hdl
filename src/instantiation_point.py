
import inspect
import os
from types import FrameType
from typing import Optional
from frame_info import FrameInfo, FrameInfoFactory

class InstantiationPoint:
    
    frame_info: FrameInfo

    def __init__(self, current_frame: Optional[FrameType] = None) -> None:
        if current_frame is None:
            current_frame = inspect.currentframe()
        self.frame_info = FrameInfoFactory().get_frame_info(current_frame=current_frame)

    def show(self) -> str:
        file_name = "unknown"
        if self.frame_info.file_name is not None:
            file_name = os.path.basename(self.frame_info.file_name)
        return f"{file_name}({self.frame_info.line_number})"
