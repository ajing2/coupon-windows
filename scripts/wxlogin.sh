#!/bin/bash

if [ $# -lt 2 ]; then
    echo -e "usages: \n\t$0 uuid-path qr-path\n"
    exit 1
fi

DIR=$(dirname "$0")

APP=$(basename "$0")
APP=${APP//\.sh/.py}

cd $DIR/../ \
&& source env/bin/activate \
&& python $APP $@

