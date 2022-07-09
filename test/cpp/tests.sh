#!/bin/bash

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

filter=$1

test_files=$(find $SCRIPTPATH -name *.cpp | grep -v "_test.cpp")

vhdl_path=$(realpath $SCRIPTPATH/../../vhdl)

RETURN_CODE=0

for i in $test_files; do
    if [[ "$i" == *"$filter"* ]]; then
	file_name=$(realpath $i)
	command="$vhdl_path/compile.sh $file_name"
	echo -n "$command : "
	eval "$command" > /dev/null
	EXIT_CODE=$?
	if [ $EXIT_CODE -eq 0 ]; then
	    echo "OK"
	else
	    echo "FAILED"
	    echo $TEST_OUTPUT
	    RETURN_CODE=1
	fi
    fi
done

test_files=$(find $SCRIPTPATH -name *.cpp | grep "_test.cpp")

for i in $test_files; do
    if [[ "$i" == *"$filter"* ]]; then
	file_name=$(realpath $i)
	command="$vhdl_path/test.sh $file_name"
	echo -n "$command : "
	TEST_OUTPUT=$(eval "$command")
	EXIT_CODE=$?
	if [ $EXIT_CODE -eq 0 ]; then
	    echo "OK"
	else
	    echo "FAILED"
	    echo $TEST_OUTPUT
	    echo "To debug problem use: gtkwave $(dirname $file_name)/output.vcd"
	    RETURN_CODE=1
	fi
    fi
done

exit $RETURN_CODE

