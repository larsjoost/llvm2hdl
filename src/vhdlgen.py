from typing import List, Optional

from file_writer import FileContents, FileGenerator, FilePrinter
from function_parser import FunctionParser
from instance_statistics import InstanceStatistics
from llvm_parser import LlvmModule

class VhdlGen:

    def parse(self, module: LlvmModule, file_handle: FileGenerator, statistics: InstanceStatistics) -> None:
        module.write_constants(file_writer=file_handle)
        file_printer = FilePrinter()
        for function in module.functions:
            function_parser = FunctionParser()
            file_contents: FileContents = function_parser.parse(function=function, file_handle=file_handle, statistics=statistics)    
            file_printer.generate(contents=file_contents)