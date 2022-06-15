import unittest

from llvm_parser import LlvmParser

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
        a = "%call = call i32 @_Z3addii(i32 2, i32 3)"
        b = x.get_call_assignment(a)
        self.assertEqual(b.reference, "%call")
        self.assertEqual(b.name, "@_Z3addii")
        self.assertEqual(b.arguments, ["2", "3"])

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
        self.assertEqual(b.opcode, "add")
        self.assertEqual(b.data_type, "i32")
        self.assertEqual(b.data_width, 32)
        self.assertEqual(b.operands[0], "%0")
        self.assertEqual(b.operands[1], "%1")
        
if __name__ == "__main__":
    unittest.main()
