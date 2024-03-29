#!/bin/bash

set -e

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

echo "Checking with mypy"
mypy src/*.py

echo "Checking code quality"
xenon -b A -a A src/

echo "Checking with ruff"
ruff check src/*.py

echo "Running unit tests"
$SCRIPTPATH/unit_tests.sh

echo "Running module test"
$SCRIPTPATH/test/cpp/tests.sh
