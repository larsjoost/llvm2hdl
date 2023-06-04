
class VhdlIncludeLibraries:

   def get(self) -> str:
        return """

library ieee;
use ieee.std_logic_1164.all;

library llvm;
use llvm.llvm_pkg.conv_std_ulogic_vector;
use llvm.llvm_pkg.get;
use llvm.llvm_pkg.integer_array_t;
use llvm.llvm_pkg.set_initialization;
use llvm.llvm_pkg.to_std_ulogic_vector;
use llvm.llvm_pkg.to_real;

library memory;

library work;
        
        """
        