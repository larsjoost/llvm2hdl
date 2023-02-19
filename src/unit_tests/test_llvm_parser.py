import unittest
from instruction import GetelementptrInstruction
from instruction_argument import InstructionArgument
from llvm_declarations import LlvmIntegerDeclaration, LlvmPointerDeclaration

from llvm_type import LlvmInteger, LlvmVariableName
from llvm_parser import ConstantContainer, GetelementptrInstructionParser, InstructionParserArguments, LlvmArgumentParser

from messages import Messages

class TestGetelementptrInstructionParser(unittest.TestCase):        

    def test_parse(self):
        x = GetelementptrInstructionParser()
        instruction = "getelementptr inbounds [4 x i32], ptr %n, i64 0, i64 1"
        destination = LlvmVariableName(name='%arrayidx')
        constants = ConstantContainer(declarations=[])
        expected = GetelementptrInstruction(opcode='getelementptr', data_type=LlvmPointerDeclaration(), operands=[InstructionArgument(signal_name=LlvmVariableName(name='%n'), data_type=LlvmPointerDeclaration(), unnamed=False, port_name=None)], offset=1)
        got = x.parse(arguments=InstructionParserArguments(instruction=instruction, destination=destination, constants=constants))
        self.assertEqual(got, expected)
        
class TestArgumentParser(unittest.TestCase):        

    def test_argument_parser(self):
        x = LlvmArgumentParser()
        arguments = "i32 2, i32* nonnull %n"
        expected = [InstructionArgument(signal_name=LlvmInteger(value=2), data_type=LlvmIntegerDeclaration(data_width=32), unnamed=False, port_name=None), InstructionArgument(signal_name=LlvmVariableName(name='%n'), data_type=LlvmPointerDeclaration(), unnamed=False, port_name=None)]
        got = x.parse(arguments=arguments)
        self.assertEqual(got, expected)
        arguments = "ptr nocapture noundef readonly %a"
        expected = [InstructionArgument(signal_name=LlvmVariableName(name='%a'), data_type=LlvmPointerDeclaration(), unnamed=False, port_name=None)]
        got = x.parse(arguments=arguments)
        self.assertEqual(got, expected)
        
if __name__ == "__main__":
    unittest.main()
