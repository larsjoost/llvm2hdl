import inspect
import os

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
        print(f"{os.path.basename(frame_info.file_name)}({frame_info.line_number}): {func.__name__}( {func_args_str} )", end="")
        result = func(*args, **kwargs)
        print(f" = {result}")
        return result

    return wrapper
