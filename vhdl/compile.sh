#!/bin/bash

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

function error {
    local message=$1
    echo "#ERROR ($(basename $SCRIPT)): $message" 1!>2
}

while getopts 'hv' opt; do
  case "$opt" in
    v)
	set -x
	VERBOSE="-v"
	;;
    ?|h)
      echo "Usage: $(basename $0) [-v] file_name"
      exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"

file_name=$(realpath $1)

if [ -z "$file_name" ]; then
    error "File name must be specified"
    exit 1
fi

set -e

lib_path=$SCRIPTPATH/../lib

llvm_path=$lib_path/llvm
memory_path=$lib_path/memory

file_path=$(dirname $file_name)

ghdl_arguments="--std=08 -Wno-hide"

cd $file_path

$SCRIPTPATH/../cpp2hdl.sh $VERBOSE $file_name
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
