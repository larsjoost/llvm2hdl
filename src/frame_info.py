
from dataclasses import dataclass
import os
from typing import Optional
from types import FrameType

@dataclass
class FrameInfo:
    file_name: Optional[str] = None
    function_name: Optional[str] = None
    line_number: Optional[int] = None


class FrameInfoFactory:
    
    def get_frame_info(self, current_frame: Optional[FrameType]) -> FrameInfo:
        result = FrameInfo()
        if current_frame is not None:
            previous_frame = current_frame.f_back
            if previous_frame is not None:
                line_number = previous_frame.f_lineno
                file_name = previous_frame.f_code.co_filename
                function_name = os.path.basename(previous_frame.f_code.co_name)
                result = FrameInfo(file_name=file_name, function_name=function_name, line_number=line_number)
        return result
