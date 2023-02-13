#!/bin/bash

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

CONTAINER_NAME=llvm2hdl

# docker build -t $CONTAINER_NAME -f $SCRIPTPATH/Dockerfile

MOUNT_SCRIPTPATH="-v $SCRIPTPATH:$SCRIPTPATH"

MOUNT="$MOUNT_SCRIPTPATH"

#docker run -it $MOUNT -w $(pwd) $CONTAINER_NAME python llvm2hdl.py $@

python3 $SCRIPTPATH/llvm2hdl.py $@
