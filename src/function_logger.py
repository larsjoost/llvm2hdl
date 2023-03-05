import inspect
import os
from typing import Any, Optional, Union, List

from color_text import ColorText, HighLight
from frame_info import FrameInfoFactory

def log_entry_and_exit(highlight: Optional[Union[List[str], str]] = None, trigger: Optional[str] = None):
    """
    Decorator to print function call details.

    This includes parameters names and effective values.
    """
    def decorator(func):

        def _get_argument(key, value) -> str:
            x = ColorText(key, "yellow")
            return f"{x} = {value}"

        def _print_function_call(file_name: str, line_number: int, function_name: str, func_args_str: str) -> None:
            function_name = str(ColorText(function_name, "blue"))
            function_arguments = HighLight().highlight_replace(text=func_args_str, highlight=highlight)
            function_call = f"{file_name}({line_number}): {function_name}( {function_arguments} ) ="
            print(function_call)

        def _print_function_result(result: Any) -> None:
            result_text = str(ColorText(str(result), "magenta"))
            result_text = HighLight().highlight_replace(text=result_text, highlight=highlight)
            print(result_text)

        def wrapper(*args, **kwargs):
            frame_info = FrameInfoFactory().get_frame_info(current_frame=inspect.currentframe())
            func_args = inspect.signature(func).bind(*args, **kwargs).arguments
            func_args_str = ", ".join(_get_argument(key=key, value=value) for key, value in func_args.items())
            file_name = os.path.basename(frame_info.file_name)
            line_number = frame_info.line_number
            enable_output = (trigger is None) or (trigger in func_args_str)
            if enable_output:
                _print_function_call(file_name=file_name, line_number=line_number, function_name=func.__name__, func_args_str=func_args_str)
            result = func(*args, **kwargs)  
            if enable_output:
                _print_function_result(result=result)
            return result

        return wrapper

    return decorator
