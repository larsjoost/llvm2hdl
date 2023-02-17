import inspect
import os

from color_text import ColorText
from frame_info import FrameInfoFactory

def log_entry_and_exit(func):
    """
    Decorator to print function call details.

    This includes parameters names and effective values.
    """

    def _get_argument(key, value) -> str:
        x = ColorText(key, "yellow")
        return f"{x} = {value}"

    def wrapper(*args, **kwargs):
        frame_info = FrameInfoFactory().get_frame_info(current_frame=inspect.currentframe())
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(_get_argument(key=key, value=value) for key, value in func_args.items())
        file_name = os.path.basename(frame_info.file_name)
        line_number = frame_info.line_number
        function_name = ColorText(func.__name__, "blue")
        try:
            result = func(*args, **kwargs)  
        except Exception as e:
            print(f"{file_name}({line_number}): {function_name}( {func_args_str} )")
            raise e from e
        result_text = ColorText(str(result), "magenta")
        print(f"{file_name}({line_number}): {function_name}( {func_args_str} ) = {result_text}")
        return result

    return wrapper
