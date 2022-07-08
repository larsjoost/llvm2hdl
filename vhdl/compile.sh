#!/bin/bash

file_name=$(realpath $1)

set -e

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

llvm_path=$SCRIPTPATH/../lib/llvm

file_path=$(dirname $file_name)

ghdl_arguments="--std=08"

cd $file_path

$SCRIPTPATH/../cpp2hdl.sh $file_name
instances_file_name=${file_name%.cpp}.inc
instances=$(cat $instances_file_name)
common_instances="llvm_pkg llvm_buffer"
instances=$(echo "$common_instances $instances")
for i in $instances; do
    ghdl -i $ghdl_arguments --work=llvm $llvm_path/$i.vhd
done
vhdl_file_name=${file_name%.cpp}.vhd
ghdl -i $ghdl_arguments --work=work $vhdl_file_name

cd -
