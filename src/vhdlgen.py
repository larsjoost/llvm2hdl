from typing import List

from file_writer import FunctionContents, VhdlFunctionGenerator, FilePrinter
from function_parser import FunctionParser
from llvm_parser import LlvmModule
from function_logger import log_entry_and_exit
from vhdl_function_definition import VhdlFunctionDefinitionFactory

class VhdlGen:

    def parse(self, file_name: str, module: LlvmModule, file_handle: VhdlFunctionGenerator) -> None:
        module.write_constants(file_writer=file_handle)
        module.write_references(file_writer=file_handle)
        file_contents: List[FunctionContents] = []
        for function in module.functions.functions:
            parsed_functions = FunctionParser().parse(function=function)
            translated_vhdl_function = VhdlFunctionDefinitionFactory().get(function_definition=parsed_functions)
            file_contents.append(file_handle.write_function(function=translated_vhdl_function))    
        file_printer = FilePrinter()
        file_printer.generate(file_name=file_name, contents=file_contents)
