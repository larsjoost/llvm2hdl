
import inspect
from frame_info import FrameInfo, FrameInfoFactory

class InstantiationPoint:
    
    frame_info: FrameInfo

    def __init__(self) -> None:
        self.frame_info = FrameInfoFactory().get_frame_info(current_frame=inspect.currentframe())

    def __str__(self) -> str:
        return f"{self.frame_info.file_name}({self.frame_info.line_number})"
