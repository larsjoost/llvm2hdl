#!/bin/bash

file_name=$(realpath $1)

set -e

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

file_path=$(dirname $file_name)

ghdl_arguments="--std=08"

cd $file_path

$SCRIPTPATH/cpp2hdl.sh $file_name
instances_file_name=${file_name%.cpp}.inc
instances=$(cat $instances_file_name)
instances=$(echo "llvm_pkg $instances")
for i in $instances; do
    ghdl -i $ghdl_arguments --work=llvm $SCRIPTPATH/lib/llvm/$i.vhd
done
vhdl_file_name=${file_name%.cpp}.vhd
ghdl -i $ghdl_arguments --work=work $vhdl_file_name

cd -
