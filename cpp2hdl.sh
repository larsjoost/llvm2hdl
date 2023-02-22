#!/bin/bash

file_name=$1

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

llvm_file_name=${file_name%.cpp}.ll

include_dir=$SCRIPTPATH/lib/test

include_files=$SCRIPTPATH/lib/test/test.cpp

CONTAINER_NAME=cpp2hdl

docker build -t $CONTAINER_NAME -f $SCRIPTPATH/Dockerfile

file_path=$(dirname $file_name)

MOUNT="-v $file_path:$file_path -v $include_dir:$include_dir"

docker run -it $MOUNT -w $(pwd) $CONTAINER_NAME clang++ -S -O3 -fno-discard-value-names -emit-llvm -o $llvm_file_name -I$include_dir $file_name 

$SCRIPTPATH/src/llvm2hdl.sh -f $llvm_file_name 
