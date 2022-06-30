from typing import List, Optional
from llvmlite.binding import ModuleRef

from file_writer import FileWriter
from function_parser import FunctionParser
from global_variables import GlobalVariables
from instance_statistics import InstanceStatistics

class VhdlGen:

    def parse(self, module: ModuleRef, file_handle: FileWriter, statistics: InstanceStatistics):
        global_variables = GlobalVariables()
        for global_variable in module.global_variables:
            global_variables.add(name=global_variable.name, data_type=global_variable.type,
            definition=str(global_variable))
        for function in module.functions:
            function_parser = FunctionParser()
            function_parser.parse(function=function, global_variables=global_variables, 
            file_handle=file_handle, statistics=statistics)
        
    def print_tree(self, m: ModuleRef):
        for function in m.functions:
            print(f'Function: {function.name}/`{function.type}`')
            assert function.module is m
            assert function.function is None
            assert function.block is None
            assert function.is_function and not (function.is_block or function.is_instruction)
            print(f'Function attributes: {list(function.attributes)}')
            for argument in function.arguments:
                print(f'Argument: {argument.name}/`{argument.type}`')
                print(f'Argument attributes: {list(argument.attributes)}')
            for block in function.blocks:
                print(f'Block: {block.name}/`{block.type}`\n{block}\nEnd of Block')
                assert block.module is m
                assert block.function is function
                assert block.block is None
                assert block.is_block and not (block.is_function or block.is_instruction)
                for instruction in block.instructions:
                    print(f'Instruction: {instruction.name}/`{instruction.opcode}`/`{instruction.type}`: `{instruction}`')
                    print(f'Attributes: {list(instruction.attributes)}')
                    assert instruction.module is m
                    assert instruction.function is function
                    assert instruction.block is block
                    assert instruction.is_instruction and not (instruction.is_function or instruction.is_block)
                    for operand in instruction.operands:
                        print(f'Operand: {operand.name}/{operand.type}')

        for global_variable in m.global_variables:
            print(f'Global: {global_variable.name}/`{global_variable.type}`')
            assert global_variable.is_global
            print(f'Attributes: {list(global_variable.attributes)}')
            print(global_variable)

    
