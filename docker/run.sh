#!/bin/bash

set -x

SCRIPT=$(readlink -f $0)
SCRIPTPATH=$(dirname $SCRIPT)

ALL_ARGUMENTS=$@

INSTALL_DIR=$HOME/bin

MOUNT_DIR="-v /opt:/opt:z -v $HOME:$HOME:z"

WORKING_DIR="-w $(pwd)"

source $SCRIPTPATH/settings.sh

usage()
{
    cat << EOF
Command: $0 $ALL_ARGUMENTS

usage: $0 -c "<string>" [-v "<string>"] [-o <path>] [-h]

OPTIONS:
   -h                          Show this message
   -c "<string>"               Execute command  
   -i <string>                 Docker image name
   -v <patg>                   Mount directory
   -o <path>                   Installation path (default = $INSTALL_DIR)
   -v                          Verbose

Example:

$0 -c "bash echo Hello" 
 
EOF
}

while getopts ":hc:i:o:v:" OPTION
do
     case $OPTION in
         c)
             COMMAND="$OPTARG"
             ;;
         i)
             DOCKER_IMAGE_NAME="$OPTARG"
             ;;
         v)
             MOINT_DIR="$MOUNT_DIR $OPTARG:$OPTARG:z"
             ;;
         o)
             INSTALL_DIR="$OPTARG"
             ;;
         h)
             usage
             exit 1
             ;;
         ?)
             error "Unknown option $OPTARG"
             usage
             exit 1
             ;;
         :)
             error "No argument value for option $OPTARG"
             usage
             exit 1
             ;;
     esac
done

source $SCRIPTPATH/start.sh

if [ ! -w $INSTALL_DIR ]; then
    error "$INSTALL_DIR is not writable"
    exit 1
fi
    
docker run -it -e PATH --rm $WORKING_DIR $MOUNT_DIR $DOCKER_IMAGE_NAME bash -c "$COMMAND"
