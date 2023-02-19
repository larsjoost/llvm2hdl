#!/bin/bash

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

BIN_PATH=$SCRIPTPATH/bin

[[ ":$PATH:" == *:${BIN_PATH}:* ]] || PATH="$PATH:${BIN_PATH}"

export PATH
