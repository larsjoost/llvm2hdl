from typing import List, Optional

from file_writer import FunctionContents, FunctionGenerator, FilePrinter
from function_parser import FunctionParser
from instance_statistics import InstanceStatistics
from llvm_parser import LlvmModule

class VhdlGen:

    def parse(self, file_name: str, module: LlvmModule, file_handle: FunctionGenerator, statistics: InstanceStatistics) -> None:
        module.write_constants(file_writer=file_handle)
        file_contents: List[FunctionContents] = []
        for function in module.functions:
            function_parser = FunctionParser()
            file_contents.append(function_parser.parse(function=function, constants=module.constants, file_handle=file_handle, statistics=statistics))    
        file_printer = FilePrinter()
        file_printer.generate(file_name=file_name, contents=file_contents)