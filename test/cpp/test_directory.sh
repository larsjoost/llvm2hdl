#!/bin/bash

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

test_directory=$1

source $SCRIPTPATH/exit_values.sh

vhdl_path=$(realpath $SCRIPTPATH/../../vhdl)

compile_file_name=$(find $test_directory -maxdepth 1 -name *.cpp | grep -v "_test.cpp")
if [ -n "$compile_file_name" ]; then
    file_name=$(realpath $compile_file_name)
    command="$vhdl_path/compile.sh $file_name"
    echo $command
    eval $command || exit $EXIT_ERROR
    test_file_name=$(find $test_directory -maxdepth 1 -name *.cpp | grep "_test.cpp")
    if [ -n "$test_file_name" ]; then
	file_name=$(realpath $test_file_name)
	command="$vhdl_path/test.sh $file_name"
	echo $command
	eval $command || exit $EXIT_ERROR
    fi
else
    exit $EXIT_EMPTY
fi

exit $EXIT_OK

