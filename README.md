
The goal of the project is to convert languages (Ada, C, C++, D, Delphi, Fortran, Haskell, Julia, Objective-C, Rust, and Swift). 
that support LLVM IR generation (https://llvm.org/docs/LangRef.html) files
to VHDL or Verilog, so that the code can be synthesized to FPGA firmware. 

The first milestone is to implement a RISC-V CPU in C++.

The current version can convert a c++ file to VHDL by typing:

./cpp2hdl.sh test/cpp/add/add.cpp

Run unit tests by typing:

./unit_tests.sh

Run C++ tests by typing:

cd test/cpp

./tests.sh

Installation:

conda install --channel=numba llvmlite

apt install clang

Install minimum ghdl version 2.0.0 from https://github.com/ghdl/ghdl or

apt install ghdl

Optional:

apt install gtkwave
