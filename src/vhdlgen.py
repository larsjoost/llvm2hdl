from typing import List

from file_writer import FunctionContents, VhdlFunctionGenerator, FilePrinter
from function_parser import FunctionParser
from llvm_function import LlvmFunction
from llvm_parser import LlvmModule
from messages import Messages
from vhdl_function_definition import VhdlFunctionDefinitionFactory

class VhdlGen:

    def __init__(self, msg: Messages) -> None:
        self._msg = msg

    def _write_function(self, function: LlvmFunction, file_generator: VhdlFunctionGenerator) -> FunctionContents:
        parsed_functions = FunctionParser().parse(function=function)
        translated_vhdl_function = VhdlFunctionDefinitionFactory().get(function_definition=parsed_functions)
        return file_generator.write_function(function=translated_vhdl_function)    

    def _generate_function(self, module: LlvmModule, function: LlvmFunction) -> FunctionContents:
        file_generator = VhdlFunctionGenerator()
        module.write_constants(file_writer=file_generator)
        module.write_references(file_writer=file_generator)
        return self._write_function(function=function, file_generator=file_generator)    

    def parse(self, file_name: str, module: LlvmModule) -> None:
        file_contents: List[FunctionContents] = [
            self._generate_function(module=module, function=function)
            for function in module.functions.functions
        ]
        file_printer = FilePrinter()
        file_printer.generate(file_name=file_name, contents=file_contents)
