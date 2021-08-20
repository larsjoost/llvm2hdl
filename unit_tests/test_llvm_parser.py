import unittest

from llvm_parser import LlvmParser

class TestSourceParser(unittest.TestCase):

    def test_getReturnInstruction(self):
        x = LlvmParser()
        a = "ret i32 %add"
        b = x.getReturnInstruction(a)
        self.assertEqual(b.data_width, 32)
        self.assertEqual(b.data_type, "i32")
        self.assertEqual(b.value, "%add")
        
    def test_getAssignment(self):
        x = LlvmParser()
        a = "store i32 %a, i32* %a.addr, align 4"
        b = x.getAssignment(a)
        self.assertEqual(b.destination, "%a.addr")
        self.assertEqual(b.source, "%a")
        a = "%0 = load i32, i32* %a.addr, align 4"
        b = x.getAssignment(a)
        self.assertEqual(b.destination, "%0")
        self.assertEqual(b.source, "%a.addr")
    
if __name__ == "__main__":
    unittest.main()
