#!/bin/bash

SOURCE=/tmp/serialsource0
SINK=/tmp/serialsink0

socat -d -d pty,raw,echo=0,link=$SOURCE pty,raw,echo=0,link=$SINK &
python flipsimulator.py $SOURCE &
python flipstudio.py $SINK &