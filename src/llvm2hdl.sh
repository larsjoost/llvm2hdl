#!/bin/bash

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

ALL_ARGUMENTS=$@

while getopts ":f:" o; do
    case "${o}" in
        f)
            file_name=${OPTARG}
	    ;;
        *)
            ;;
    esac
done

CONTAINER_NAME=llvm2hdl

cd $SCRIPTPATH
docker build -t $CONTAINER_NAME .
cd -

MOUNT_SCRIPTPATH="-v $SCRIPTPATH:$SCRIPTPATH"

FILE_PATH="$(dirname $file_name)"

MOUNT_FILE_PATH="-v $FILE_PATH:$FILE_PATH"

MOUNT="$MOUNT_SCRIPTPATH $MOUNT_FILE_PATH"

docker run -it $MOUNT -w $(pwd) $CONTAINER_NAME python3 $SCRIPTPATH/llvm2hdl.py $ALL_ARGUMENTS
