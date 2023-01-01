from dataclasses import dataclass
import inspect
import sys
import os
from types import FrameType
from typing import Optional, Union

from color_text import ColorText
from frame_info import FrameInfoFactory


class Messages:

    _verbose: bool = False
    _note_enable: bool = True
    _indent: int = 0
    
    def __init__(self, verbose: bool = False):
        self._verbose = verbose
        self._note_enable = True
        self._indent = 0

    def set_verbose(self, verbose):
        self._verbose = verbose

    def _print_formatted(self, color_text: Union[ColorText, str], text: str, current_frame: Optional[FrameType]):
        frame_info = FrameInfoFactory().get_frame_info(current_frame=current_frame)
        base_name = None if frame_info.file_name is None else os.path.basename(frame_info.file_name)
        indent = " " * self._indent
        print(f"{indent}[{str(color_text)}, {str(base_name)}({str(frame_info.line_number)})] {text}")
        sys.stdout.flush()

    def debug(self, text, verbose=False):
        if self._verbose or verbose:
            current_frame = inspect.currentframe()
            self._print_formatted(color_text="DEBUG", text=str(text), 
            current_frame=current_frame)

    def note(self, text):
        if self._note_enable and self._verbose is not None:
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
            current_frame = inspect.currentframe()
            self._print_formatted(color_text=ColorText("ERROR", "error"),
                                text=text, current_frame=current_frame)

    def function_start(self, text: str = "", verbose=False):
        if self._verbose or verbose:
            current_frame = inspect.currentframe()
            frame_info = FrameInfoFactory().get_frame_info(current_frame=current_frame)
            function_name = str(frame_info.function_name)
            text = f"{function_name}({text})"
            self._print_formatted(color_text=ColorText("FUNCTION START", "magenta"),
            text=text, current_frame=current_frame)
            self._indent += 2

    def function_end(self, return_value=None, verbose=False):
        if self._verbose or verbose:
            current_frame = inspect.currentframe()
            frame_info = self.get_frame_info(current_frame)
            self._indent = self._indent - 2
            function_name = str(frame_info.function_name)
            text = f"{function_name} = {str(return_value)}"
            self._print_formatted(color_text=ColorText("FUNCTION END", "magenta"), text=text, current_frame=current_frame)
