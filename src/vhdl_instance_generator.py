from vhdl_function import VhdlFunction
from vhdl_function_container import VhdlFunctionContainer
from vhdl_function_contents import VhdlFunctionContents
from vhdl_generator import VhdlGenerator
from vhdl_memory_generator import VhdlMemoryGenerator
from vhdl_module import VhdlModule


class VhdlInstanceGenerator:
    
    def generate_code(self, function: VhdlFunction, function_contents: VhdlFunctionContents, module: VhdlModule) -> None: 
        external_pointer_names = module.get_external_pointer_names()
        instructions = function.get_instructions()
        VhdlGenerator().generate_code(instructions=instructions, external_pointer_names=external_pointer_names, function_contents=function_contents, module=module)
        memory_names = function.get_memory_names()
        memory_instance_names = function.get_memory_instance_names()
        VhdlMemoryGenerator().generator_code(memory_names=memory_names, memory_instance_names=memory_instance_names, function_contents=function_contents)
