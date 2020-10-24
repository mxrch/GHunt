#!/bin/bash
docker run -v $(pwd)/resources:/usr/src/app/resources -ti ghunt hunt.py $1
