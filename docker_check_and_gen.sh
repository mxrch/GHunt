#!/bin/bash
docker run -v ghunt-resources:/usr/src/app/resources -ti ghcr.io/mxrch/ghunt check_and_gen.py
