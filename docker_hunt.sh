#!/bin/bash
docker run -v ghunt-resources:/usr/src/app/resources -ti mxrch/ghunt hunt.py $1
