from typing import List

from file_writer import FunctionContents, FunctionGenerator, FilePrinter
from function_parser import FunctionParser
from llvm_parser import LlvmModule
from function_logger import log_entry_and_exit

class VhdlGen:

    def parse(self, file_name: str, module: LlvmModule, file_handle: FunctionGenerator) -> None:
        module.write_constants(file_writer=file_handle)
        module.write_references(file_writer=file_handle)
        file_contents: List[FunctionContents] = []
        for function in module.functions:
            function_parser = FunctionParser()
            file_contents.append(function_parser.parse(function=function, file_handle=file_handle))    
        file_printer = FilePrinter()
        file_printer.generate(file_name=file_name, contents=file_contents)
