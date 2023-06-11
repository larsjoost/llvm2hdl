#!/bin/bash
LOGIN_USER=${LOGIN_USER:-user}
USER_ID=${LOCAL_UID:-1000}
GROUP_ID=${LOCAL_GID:-1000}
useradd -u $USER_ID -o -m $LOGIN_USER
export HOME=/home/$LOGIN_USER
exec /usr/sbin/gosu $LOGIN_USER "$@"
