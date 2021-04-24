#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ $# -ge 1 ]
then
    python3 $DIR/crawler.py -n $1 -c $DIR/config.json http://results.o2cm.com
else
    python3 $DIR/crawler.py -n 1 -c $DIR/config.json http://results.o2cm.com
fi
