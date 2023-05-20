from typing import List

from vhdl_function_contents import VhdlFunctionContents
from vhdl_file_printer import VhdlFilePrinter
from llvm_parser import LlvmModule
from vhdl_module import VhdlModule

class VhdlGen:

    def parse(self, file_name: str, module: LlvmModule) -> None:
        vhdl_module = VhdlModule(module=module)
        file_contents: List[VhdlFunctionContents] = vhdl_module.generate_code()
        file_printer = VhdlFilePrinter()
        file_printer.generate(file_name=file_name, contents=file_contents)
