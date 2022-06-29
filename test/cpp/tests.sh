#!/bin/bash

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

test_files=$(find $SCRIPTPATH -name *.cpp | grep -v "_test.cpp")

vhdl_path=$(realpath $SCRIPTPATH/../../vhdl)

for i in $test_files; do
    $vhdl_path/compile.sh $(realpath $i) > /dev/null || exit 1
done

test_files=$(find $SCRIPTPATH -name *.cpp | grep "_test.cpp")

RETURN_CODE=0

for i in $test_files; do
    echo -n "Testing $i: "
    TEST_OUTPUT=$($vhdl_path/test.sh $(realpath $i))
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
	echo "OK"
    else
	echo "FAILED"
	echo $TEST_OUTPUT
	RETURN_CODE=1
    fi
done

exit $RETURN_CODE

