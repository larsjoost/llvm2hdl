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
wave_file_name=${file_path}/output.ghw

ghdl_arguments="--std=08 -Wno-hide"

cd $file_path

ghdl -i $ghdl_arguments $SCRIPTPATH/../lib/test/test_main.vhd

ghdl -m $ghdl_arguments test_main

ghdl -e $ghdl_arguments test_main

ghdl -r $ghdl_arguments test_main --vcd=${vcd_file_name} --wave=${wave_file_name}

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    error "Simulation failed"
    echo "To debug problem use: gtkwave $wave_file_name or gtkwave $vcd_file_name"
    exit 1
fi

cd -
