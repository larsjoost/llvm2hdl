
The goal of the project is to convert languages (Ada, C, C++, D, Delphi, Fortran, Haskell, Julia, Objective-C, Rust, and Swift)
that support LLVM IR generation (https://llvm.org/docs/LangRef.html) files
to VHDL or Verilog, so that the code can be synthesized to FPGA firmware. The current version can convert a c++ file to VHDL by typing:

./cpp2hdl.sh test/cpp/add/add.cpp

Run unit tests by typing:

./unit_tests.sh

Installation:

pip3 install llvmlite

apt install clang ghdl
