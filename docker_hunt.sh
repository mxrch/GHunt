#!/bin/bash
docker run -v ghunt-resources:/usr/src/app/resources -ti ghcr.io/mxrch/ghunt ghunt.py $1 $2