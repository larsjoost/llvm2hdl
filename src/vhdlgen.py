from typing import List

from file_writer import VhdlFunctionContents, VhdlFunctionGenerator, FilePrinter
from function_parser import FunctionParser
from llvm_function import LlvmFunction
from llvm_globals_container import GlobalsContainer
from llvm_parser import LlvmModule
from vhdl_function_definition import VhdlFunctionDefinitionFactory

class VhdlGen:

    def _write_function(self, function: LlvmFunction, file_generator: VhdlFunctionGenerator, globals: GlobalsContainer) -> VhdlFunctionContents:
        parsed_functions = FunctionParser().parse(function=function)
        translated_vhdl_function = VhdlFunctionDefinitionFactory().get(function_definition=parsed_functions, globals=globals)
        return file_generator.write_function(function=translated_vhdl_function)    

    def _generate_function(self, module: LlvmModule, function: LlvmFunction) -> VhdlFunctionContents:
        file_generator = VhdlFunctionGenerator()
        module.write_globals(file_writer=file_generator)
        return self._write_function(function=function, file_generator=file_generator, globals=module.globals)    

    def parse(self, file_name: str, module: LlvmModule) -> None:
        file_contents: List[VhdlFunctionContents] = [
            self._generate_function(module=module, function=function)
            for function in module.functions.functions
        ]
        file_printer = FilePrinter()
        file_printer.generate(file_name=file_name, contents=file_contents)
