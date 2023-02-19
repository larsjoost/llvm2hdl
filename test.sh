#!/bin/bash

set -e

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

$SCRIPTPATH/install.sh

$SCRIPTPATH/test_all.sh

