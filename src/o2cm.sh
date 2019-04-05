#!/bin/bash

if [ $# -ge 1 ]
then
    python3 crawler.py -n $1 -c config.json http://results.o2cm.com
else
    python3 crawler.py -n 1 -c config.json http://results.o2cm.com
fi
