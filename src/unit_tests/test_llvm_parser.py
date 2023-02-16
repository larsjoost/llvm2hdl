import unittest

from llvm_type import LlvmVariableName
from llvm_parser import ConstantContainer, GetelementptrInstructionParser, InstructionParserArguments, LlvmArgumentParser

class TestGetelementptrInstructionParser(unittest.TestCase):        

    def test_parse(self):
        x = GetelementptrInstructionParser()
        instruction = "getelementptr inbounds [4 x i32], ptr %n, i64 0, i64 1"
        destination = LlvmVariableName(name='%arrayidx')
        constants = ConstantContainer(constant_declarations=[])
        print(x.parse(arguments=InstructionParserArguments(instruction=instruction, destination=destination, constants=constants)))

class TestArgumentParser(unittest.TestCase):        

    def test_argument_parser(self):
        x = LlvmArgumentParser()
        arguments = "i32 2, i32* nonnull %n"
        print(x.parse(arguments=arguments))
        arguments = "ptr nocapture noundef readonly %a"
        print(x.parse(arguments=arguments))
        
if __name__ == "__main__":
    unittest.main()
