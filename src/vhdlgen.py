from typing import List, Optional

from file_writer import FunctionContents, FunctionGenerator, FilePrinter
from function_parser import FunctionParser
from instance_statistics import InstanceStatistics
from llvm_parser import LlvmModule

class VhdlGen:

    def parse(self, file_name: str, module: LlvmModule, file_handle: FunctionGenerator) -> None:
        module.write_constants(file_writer=file_handle)
        file_contents: List[FunctionContents] = []
        for function in module.functions:
            function_parser = FunctionParser()
            file_contents.append(function_parser.parse(function=function, file_handle=file_handle))    
        file_printer = FilePrinter()
        file_printer.generate(file_name=file_name, contents=file_contents)