import inspect
import os

from color_text import ColorText
from frame_info import FrameInfoFactory

def log_entry_and_exit(func):
    """
    Decorator to print function call details.

    This includes parameters names and effective values.
    """

    def wrapper(*args, **kwargs):
        frame_info = FrameInfoFactory().get_frame_info(current_frame=inspect.currentframe())
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
        result = func(*args, **kwargs)
        file_name = os.path.basename(frame_info.file_name)
        line_number = frame_info.line_number
        result_text = ColorText(str(result), "magenta")
        print(f"{file_name}({line_number}): {func.__name__}( {func_args_str} ) = {result_text}")
        return result

    return wrapper
