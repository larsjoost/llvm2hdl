import unittest
from llvm_declarations import LlvmDeclarations

from llvm_parser import InstructionArgument, LlvmParser

class TestSourceParser(unittest.TestCase):

    def test_getReturnInstruction(self):
        x = LlvmParser()
        a = "ret i32 %add"
        b = x.get_return_instruction(a)
        self.assertEqual(b.data_width, 32)
        self.assertEqual(b.data_type, "i32")
        self.assertEqual(b.value, "%add")
        
    def test_getStoreAssignment(self):
        x = LlvmParser()
        a = "store i32 %a, i32* %a.addr, align 4"
        b = x.get_store_assignment(a)
        self.assertEqual(b.destination, "%a.addr")
        self.assertEqual(b.source, "%a")
    
    def test_getLoadAssignment(self):
        x = LlvmParser()
        a = "%0 = load i32, i32* %a.addr, align 4"
        b = x.get_load_assignment(a)
        self.assertEqual(b.destination, "%0")
        self.assertEqual(b.source, "%a.addr")
    
    def test_getCallAssignment(self):
        x = LlvmParser()
        a = "call i32 @_Z3addii(i32 2, i32 3)"
        b = x.get_call_assignment(a)
        self.assertEqual(b.opcode, "entity_Z3addii")
        data_width = LlvmDeclarations(data_type="i32")
        self.assertEqual(b.operands, [InstructionArgument(signal_name="2", data_width=data_width),
        InstructionArgument(signal_name="3", data_width=data_width)])

    def test_getReturnInstruction(self):
        x = LlvmParser()
        a = "ret i32 %add"
        b = x.get_return_instruction(a)
        self.assertEqual(b.value, "%add")
        self.assertEqual(b.data_type, "i32")
        self.assertEqual(b.data_width, 32)

    def test_getEqualAssignment(self):
        x = LlvmParser()
        a = "%0 = load i32, i32* %a.addr, align 4"
        b = x.get_equal_assignment(a)
        self.assertEqual(b.destination, "%0")
        self.assertEqual(b.source, "load i32, i32* %a.addr, align 4")
        a = "ret i32 %add"
        b = x.get_equal_assignment(a)
        self.assertEqual(b.destination, None)
        self.assertEqual(b.source, "ret i32 %add")
        
    def test_getInstruction(self):
        x = LlvmParser()
        a = "add nsw i32 %0, %1"
        b = x.get_instruction(a)
        self.assertEqual(b.opcode, "llvm_add")
        self.assertEqual(b.data_type, LlvmDeclarations(data_type="i32"))
        self.assertEqual(b.data_width, 32)
        self.assertEqual(b.operands[0], InstructionArgument(signal_name="%0", data_width=32, port_name="a"))
        self.assertEqual(b.operands[1], InstructionArgument(signal_name="%1", data_width=32, port_name="b"))
        
if __name__ == "__main__":
    unittest.main()
