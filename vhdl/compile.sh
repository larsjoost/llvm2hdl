#!/bin/bash

file_name=$(realpath $1)

set -e

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

lib_path=$SCRIPTPATH/../lib

llvm_path=$lib_path/llvm
memory_path=$lib_path/memory

file_path=$(dirname $file_name)

ghdl_arguments="--std=08 -Wno-hide"

cd $file_path

$SCRIPTPATH/../cpp2hdl.sh $file_name
instances_file_name=${file_name%.cpp}.inc
instances=$(cat $instances_file_name)
common_llvm_instances="llvm_pkg llvm_buffer"
llvm_instances=$(echo "$common_llvm_instances $instances")
for i in $llvm_instances; do
    ghdl -i $ghdl_arguments --work=llvm $llvm_path/$i.vhd
done
memory_instances=$(echo "arbiter ram")
for i in $memory_instances; do
    ghdl -i $ghdl_arguments --work=memory $memory_path/$i.vhd
done
vhdl_file_name=${file_name%.cpp}.vhd
ghdl -i $ghdl_arguments --work=work $vhdl_file_name

cd -
