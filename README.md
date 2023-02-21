
The goal of the project is to convert languages (Ada, C, C++, D, Delphi, Fortran, Haskell, Julia, Objective-C, Rust, and Swift). 
that support LLVM IR generation (https://llvm.org/docs/LangRef.html) files
to VHDL or Verilog, so that the code can be synthesized to FPGA firmware. 

The first milestone is to implement a RISC-V CPU in C++.

The current version can convert a C++ file to VHDL by typing (LLVM2HDL variable points to llvm2hdl installation directory):

source $LLVM2HDL/setup.sh

cpp2vhdl test/cpp/add/add.cpp

Run tests by typing:

cd $LLVM2HDL; ./tests.sh

Installation:

cd $LLVM2HDL; ./install.sh

