#!/bin/bash
docker run -v $(pwd)/resources:/usr/src/app/resources -ti ghunt check_and_gen.py
