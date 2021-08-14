#!/bin/bash

file_name=$1

llvm_file_name=${file_name%.cpp}.ll

clang++ -S -fno-discard-value-names -emit-llvm -o $llvm_file_name $file_name 

go_files=$(find ./ -name "*.go")

go run $go_files $llvm_file_name
