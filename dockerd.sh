#!/bin/sh
exec 1>>$DOCKER_LOGFILE
exec 2>&1
exec /usr/sbin/dockerd "$@"
