#!/bin/bash

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

VHDL_PATH=$(realpath $SCRIPTPATH/../../../../../vhdl)

IMAGE_NAME=riscv-gnu-toolchain-docker

IMAGE_EXISTS=$(docker images -q $IMAGE_NAME)

if [ -z "$IMAGE_EXISTS" ]; then
    echo "Count not find image $IMAGE_NAME. Builing Docker image..."
    cd $SCRIPTPATH/riscv-gnu-toolchain-docker
    docker build -t $IMAGE_NAME .
    cd -
fi

echo "Compiling test code test1.cpp"
docker run --rm -v $PWD:/work $IMAGE_NAME riscv32-unknown-elf-gcc -march=rv32g -O3 -c test1.cpp

echo "Converting test code to memory format"
docker run --rm -v $PWD:/work $IMAGE_NAME riscv64-unknown-elf-objcopy -O verilog -j .text test1.o binfile.v

python3 $SCRIPTPATH/verilog_to_memory.py -f binfile.v -o memory.h

echo "Compiling RISC-V rv32i test suite"
gcc -DDEBUG rv32i_test.cpp rv32i.cpp instruction_decode.cpp -o rv32i_test

echo "Testing RISC-V rv32i"
./rv32i_test

EXIT_CODE=$?

echo -n "Test "
if [ $EXIT_CODE -eq 0 ]; then
    echo "OK"
else
    echo "FAIL"
    exit 1
fi

$VHDL_PATH/compile.sh rv32i.cpp

