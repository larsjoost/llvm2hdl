from typing import List
from llvm_globals_container import GlobalsContainer
from vhdl_function import VhdlFunction
from vhdl_function_contents import VhdlFunctionContents
from vhdl_generator import VhdlGenerator
from vhdl_memory_generator import VhdlMemoryGenerator

class VhdlInstanceGenerator:
    
    def generate_code(self, function: VhdlFunction, function_contents: VhdlFunctionContents, external_pointer_names: List[str], globals: GlobalsContainer) -> None: 
        instructions = function.get_instructions()
        VhdlGenerator().generate_code(instructions=instructions, external_pointer_names=external_pointer_names, function_contents=function_contents, globals=globals)

