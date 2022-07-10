from typing import List, Optional

from file_writer import FileWriter
from function_parser import FunctionParser
from global_variables import GlobalVariables
from instance_statistics import InstanceStatistics
from llvm_parser import LlvmModule

class VhdlGen:

    def parse(self, module: LlvmModule, file_handle: FileWriter, statistics: InstanceStatistics):
        module.write_constants(file_handle=file_handle)
        for function in module.functions:
            function_parser = FunctionParser()
            function_parser.parse(function=function, file_handle=file_handle, statistics=statistics)        

    
