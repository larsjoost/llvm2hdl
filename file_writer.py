import inspect

class FileWriter:

    _debug: bool = False

    def __init__(self, file_handle):
        self._file_handle = file_handle

    def write(self, *arguments, end=None):
        if self._debug:
            line_number = inspect.currentframe().f_back.f_lineno
            file_name = inspect.currentframe().f_back.f_code.co_filename
            print(f"-- {file_name}:{line_number}:", file=self._file_handle)            
        print(*arguments, file=self._file_handle, end=end)