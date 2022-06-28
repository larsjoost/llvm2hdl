#!/bin/bash

set -e

test_files=$(find ./ -name *.cpp | grep -v test)

for i in $test_files; do
    ../../compile.sh $i > /dev/null
done

test_files=$(find ./ -name *.cpp | grep test)

for i in $test_files; do
    echo -n "Testing $i: "
    ../../test.sh $i > /dev/null
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
	echo "OK"
    else
	echo "FAILED"
    fi
done

