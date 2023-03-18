#!/bin/bash

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

source $SCRIPTPATH/exit_values.sh

filter=$1

test_directories=$(find $SCRIPTPATH -type d)

RETURN_CODE=0

NUMBER_OF_OK=0
NUMBER_OF_FAILED=0

for test_directory in $test_directories; do
    compile_file_name=$(find $test_directory -name *.cpp | grep -v "_test.cpp")
    command="$SCRIPTPATH/test_directory.sh $test_directory"
    eval "$command" > /dev/null
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq $EXIT_OK ]; then
	echo "$command : OK"
	let NUMBER_OF_OK+=1
    elif [ $EXIT_CODE -eq $EXIT_ERROR ]; then
	echo "$command : FAILED"
	echo $TEST_OUTPUT
	RETURN_CODE=1
	let NUMBER_OF_FAILED+=1
    fi
done

echo "Number of ok    : $NUMBER_OF_OK"
echo "Number of failed: $NUMBER_OF_FAILED"

exit $RETURN_CODE

