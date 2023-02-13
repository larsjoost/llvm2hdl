#!/bin/bash

set -e

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

mypy src/*.py

echo "Running unit tests"
$SCRIPTPATH/unit_tests.sh

echo "Running module test"
$SCRIPTPATH/test/cpp/tests.sh
