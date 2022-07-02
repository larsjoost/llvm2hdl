import inspect
import sys
import os

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

    def _print_formatted(self, color_text: ColorText, line_number: int, text: str, file_name: str):
        _text = text
        if len(text) > self.text_limit_size:
            _text = text[:self.text_limit_size] + "<limit size exceeded>"
        _file_name = os.path.basename(file_name)
        if len(_file_name) == 0:
            _file_name = file_name
        print(" "*self.indent + "[" + str(color_text) + ", " + _file_name + \
              "(" + str(line_number) + ")] " + _text)
        sys.stdout.flush()

    def debug(self, text, verbose=False):
        if self._verbose or verbose:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self._print_formatted(color_text="DEBUG", file_name=file_name,
                                line_number=line_number, text=str(text))

    def note(self, text):
        if self.note_enable and self._verbose is not None:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self._print_formatted(color_text=ColorText("NOTE", "note"),
                                line_number=line_number,
                                text=text, file_name=file_name)

    def warning(self, text):
        if self._verbose is not None:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self._print_formatted(color_text=ColorText("WARNING", "warning"),
                                line_number=line_number,
                                text=text, file_name=file_name)

    def error(self, text):
        if self._verbose is not None:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self._print_formatted(color_text=ColorText("ERROR", "error"), line_number=line_number,
                                text=text, file_name=file_name)

    def function_start(self, text, verbose=False):
        if self._verbose or verbose:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self._print_formatted(color_text="FUNCTION START",
                                line_number=line_number, text=text, file_name=file_name)
            self.indent += 2

    def function_end(self, text, verbose=False):
        if self._verbose or verbose:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self.indent = self.indent - 2
            self._print_formatted(color_text="FUNCTION END",
                                line_number=line_number, text=text, file_name=file_name)
