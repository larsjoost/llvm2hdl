import inspect
import sys
import os
from types import FrameType
from typing import Optional, Tuple, Union

from color_text import ColorText

class Messages:

    _verbose: bool = False
    note_enable: bool = True
    indent: int = 0
    text_limit_size: int = 1000

    def __init__(self, verbose: bool = False):
        self._verbose = verbose
        self.note_enable = True
        self.indent = 0

    def set_verbose(self, verbose):
        self._verbose = verbose

    def _get_previous_frame_info(self, current_frame: Optional[FrameType]) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        line_number = None
        file_name = None
        function_name = None
        if current_frame is not None:
            previous_frame = current_frame.f_back
            if previous_frame is not None:
                line_number = previous_frame.f_lineno
                file_name = previous_frame.f_code.co_filename
                function_name = os.path.basename(previous_frame.f_code.co_name)
        return (file_name, function_name, line_number)

    def _print_formatted(self, color_text: Union[ColorText, str], text: str, current_frame: Optional[FrameType]):
        file_name, _, line_number = self._get_previous_frame_info(current_frame)
        print(" "*self.indent + "[" + str(color_text) + ", " + str(file_name) + \
              "(" + str(line_number) + ")] " + text)
        sys.stdout.flush()

    def debug(self, text, verbose=False):
        if self._verbose or verbose:
            current_frame = inspect.currentframe()
            self._print_formatted(color_text="DEBUG", text=str(text), 
            current_frame=current_frame)

    def note(self, text):
        if self.note_enable and self._verbose is not None:
            current_frame = inspect.currentframe()
            self._print_formatted(color_text=ColorText("NOTE", "note"),
                                text=text, current_frame=current_frame)

    def warning(self, text):
        if self._verbose is not None:
            current_frame = inspect.currentframe()
            self._print_formatted(color_text=ColorText("WARNING", "warning"),
                                text=text, current_frame=current_frame)

    def error(self, text):
        if self._verbose is not None:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self._print_formatted(color_text=ColorText("ERROR", "error"), line_number=line_number,
                                text=text, file_name=file_name)

    def function_start(self, text: str = "", verbose=False):
        if self._verbose or verbose:
            current_frame = inspect.currentframe()
            _, function_name, _ = self._get_previous_frame_info(current_frame)
            text = str(function_name) + "(" + text + ")"
            self._print_formatted(color_text=ColorText("FUNCTION START", "magenta"),
            text=text, current_frame=current_frame)
            self.indent += 2

    def function_end(self, return_value=None, verbose=False):
        if self._verbose or verbose:
            current_frame = inspect.currentframe()
            _, function_name, _ = self._get_previous_frame_info(current_frame)
            self.indent = self.indent - 2
            text = str(function_name) + " = " + str(return_value)
            self._print_formatted(color_text=ColorText("FUNCTION END", "magenta"), 
            text=text, current_frame=current_frame)
