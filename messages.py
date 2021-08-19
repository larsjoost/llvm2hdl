import inspect
import sys
import os

from color_text import ColorText

class Messages:

    verbose = False
    note_enable = True
    indent = 0
    text_limit_size = 1000

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.note_enable = True
        self.indent = 0
        
    def set_verbose(self, verbose):
        self.verbose = verbose

    def printFormatted(self, type, lineNumber, text, file_name):
        t = text
        if len(text) > self.text_limit_size:
            t = text[:self.text_limit_size] + "<limit size exceeded>"
        f = os.path.basename(file_name)
        if len(f) == 0:
            f = file_name
        print(" "*self.indent + "[" + str(type) + ", " + f + \
              "(" + str(lineNumber) + ")] " + t)
        sys.stdout.flush()

    def debug(self, text, verbose=False):
        if self.verbose or verbose:
            lineNumber = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self.printFormatted(type="DEBUG", file_name=file_name,
                                lineNumber=lineNumber, text=str(text))

    def note(self, text):
        if self.note_enable and self.verbose is not None:
            lineNumber = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self.printFormatted(type=ColorText("NOTE", "note"), lineNumber=lineNumber,
                                text=text, file_name=file_name)

    def warning(self, text):
        if self.verbose is not None:
            lineNumber = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self.printFormatted(type=ColorText("WARNING", "warning"), lineNumber=lineNumber,
                                text=text, file_name=file_name)

    def error(self, text):
        if self.verbose is not None:
            lineNumber = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self.printFormatted(type=ColorText("ERROR", "error"), lineNumber=lineNumber,
                                text=text, file_name=file_name)

    def functionStart(self, text, verbose=False):
        if self.verbose or verbose:
            lineNumber = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self.printFormatted(type="FUNCTION START",
                                lineNumber=lineNumber, text=text, file_name=file_name)
            self.indent = self.indent + 2

    def functionEnd(self, text, verbose=False):
        if self.verbose or verbose:
            lineNumber = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self.indent = self.indent - 2
            self.printFormatted(type="FUNCTION END",
                                lineNumber=lineNumber, text=text, file_name=file_name)

    def functionArgument(self, text, verbose=False):
        if self.verbose or verbose:
            lineNumber = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            self.printFormatted(type="FUNCTION ARGUMENT",
                                lineNumber=lineNumber, text=text, file_name=file_name)


