#!/bin/bash

set -e

test_files=$(find ./ -name *.cpp)

for i in $test_files; do
    ../../cpp2hdl.sh $i
done

