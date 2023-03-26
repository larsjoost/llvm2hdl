
import inspect
import os
from types import FrameType
from typing import Optional

from frame_info import FrameInfoFactory


class VhdlCommentGenerator:
    def get_comment(self, current_frame: Optional[FrameType] = None) -> str:
        if current_frame is None:
            current_frame = inspect.currentframe()
        frame_info = FrameInfoFactory().get_frame_info(current_frame=current_frame)
        assert frame_info.file_name is not None
        file_name = os.path.basename(frame_info.file_name)
        return f"-- {file_name}({frame_info.line_number}): "


