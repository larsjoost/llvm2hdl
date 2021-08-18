#!/bin/bash

SCRIPT=$(readlink -f $0)
SCRIPTPATH=$(dirname $SCRIPT)
ALL_ARGUMENTS=$@

function error {
    local message=$1
    echo "#ERROR($SCRIPT): $message" 1>&2
}

source $SCRIPTPATH/settings.sh

EXECUTE="install,configure,compile,documentation"

INSTALL_DIR=$HOME/bin

usage()
{
    cat << EOF
Command: $0 $ALL_ARGUMENTS

usage: $0 [-i "<string>"] [-o <path>] [-v] [-h]

OPTIONS:
   -h                          Show this message
   -e <list>                   Execute (default = $EXECUTE) 
   -i "<text>"                 Configure parameters (default = "$INSTALL_ARGUMENTS") 
   -n <text>                   Docker image name (default = $DOCKER_IMAGE_NAME)
   -o <path>                   Installation path (default = $INSTALL_DIR)
   -v                          Verbose

Example:

$0 -c $EXECUTE -i "--prefix=/opt/panda --enable-flopoco --enable-icarus"
 
EOF
}

while getopts ":he:i:n:o:v" OPTION
do
     case $OPTION in
         e)
             EXECUTE="$OPTARG"
             ;;
         i)
             INSTALL_ARGUMENTS="$OPTARG"
             ;;
         n)
             DOCKER_IMAGE_NAME="$OPTARG"
             ;;
         o)
             INSTALL_DIR="$OPTARG"
             ;;
         h)
             usage
             exit 1
             ;;
         v)
             set -x
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

function install_docker {
    $SCRIPTPATH/rootless
}

function build_docker_image {
    local DOCKER_IMAGE_EXISTS=$(docker images -q $DOCKER_IMAGE_NAME)

    if [ -z "$DOCKER_IMAGE_EXISTS" ]; then
        docker build -t $DOCKER_IMAGE_NAME -f $SCRIPTPATH/Dockerfile .
    fi
}

SPACE_SEPARATED_EXECUTE=$(echo "$EXECUTE" | tr ',' ' ')

for i in $SPACE_SEPARATED_EXECUTE; do
     case $i in
         install)
             install_docker
             source $SCRIPTPATH/start.sh || exit $?
             build_docker_image
             if [ ! -e $HOME/bin/bambu ]; then
                 ln -s $SCRIPTPATH/bambu $HOME/bin/bambu
             fi
             ;;
         configure)
             $SCRIPTPATH/run.sh -i $DOCKER_IMAGE_NAME -c "make -f Makefile.init; mkdir -p obj; cd obj; ../configure $INSTALL_ARGUMENTS"
             ;;
         compile)
             $SCRIPTPATH/run.sh -i $DOCKER_IMAGE_NAME -c "cd obj; make; make install"
             ;;
         documentation)
             $SCRIPTPATH/run.sh -i $DOCKER_IMAGE_NAME -c "cd obj; make documentation"
             ;;
         bash)
             $SCRIPTPATH/run.sh -i $DOCKER_IMAGE_NAME -c "bash"
             ;;
         *)
             error "Unknown execute command: $i"
             usage
             exit 1
             ;;
     esac
done








