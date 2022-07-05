#!/bin/bash

file_name=$(realpath $1)

set -e

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

function error {
    local message=$1
    echo "#ERROR ($(basename $SCRIPT)): $message" 1!>2
}

$SCRIPTPATH/compile.sh $file_name

file_path=$(dirname $file_name)

vcd_file_name=${file_path}/output.vcd

ghdl_arguments="--std=08"

cd $file_path

ghdl -a $ghdl_arguments $SCRIPTPATH/../lib/test/test_main.vhd

ghdl -m $ghdl_arguments test_main

ghdl -e $ghdl_arguments test_main

ghdl -r $ghdl_arguments test_main  --vcd=${vcd_file_name}

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    error "Simulation failed"
    exit 1
fi

cd -
