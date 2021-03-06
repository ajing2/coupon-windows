#!/bin/bash

if [ $# -lt 1 ]; then
    echo -e "usages: \n\t$0 config-file [qr-path]\n"
    exit 1
fi

DIR=$(dirname "$0")
source "$DIR/command.sh"

APP=$(basename "$0")
APP=${APP//\.sh/.py}

run $APP $@

