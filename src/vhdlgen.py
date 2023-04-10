from typing import List

from vhdl_file_writer import VhdlFunctionContents, VhdlFunctionGenerator
from vhdl_file_printer import VhdlFilePrinter
from llvm_function import LlvmFunction
from llvm_parser import LlvmModule
from vhdl_function import VhdlFunction
from vhdl_module import VhdlModule

class VhdlGen:

    def _generate_function(self, module: LlvmModule, function: LlvmFunction) -> VhdlFunctionContents:
        vhdl_function = VhdlFunction(function=function)
        vhdl_module = VhdlModule(module=module)
        function_contents = VhdlFunctionContents(name=vhdl_function.get_entity_name())    
        file_generator = VhdlFunctionGenerator(function_contents=function_contents)
        module.write_globals(file_writer=file_generator)
        return file_generator.write_function(function=vhdl_function, module=vhdl_module)    

    def parse(self, file_name: str, module: LlvmModule) -> None:
        file_contents: List[VhdlFunctionContents] = [
            self._generate_function(module=module, function=function)
            for function in module.functions.functions
        ]
        file_printer = VhdlFilePrinter()
        file_printer.generate(file_name=file_name, contents=file_contents)
