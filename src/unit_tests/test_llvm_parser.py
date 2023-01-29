import unittest

from llvm_declarations import LlvmName
from llvm_parser import GetelementptrInstructionParser, LlvmArgumentParser

class TestGetelementptrInstructionParser(unittest.TestCase):        

    def test_parse(self):
        x = GetelementptrInstructionParser()
        instruction = "getelementptr inbounds [4 x i32], ptr %n, i64 0, i64 1"
        destination = LlvmName(name='%arrayidx')
        print(x.parse(instruction=instruction, destination=destination))

class TestArgumentParser(unittest.TestCase):        

    def test_argument_parser(self):
        x = LlvmArgumentParser()
        arguments = "i32 2, i32* nonnull %n"
        print(x.parse(arguments=arguments))
        arguments = "ptr nocapture noundef readonly %a"
        print(x.parse(arguments=arguments))
        
if __name__ == "__main__":
    unittest.main()
