#!/bin/bash

set -x
parallel pypy3 ./main.py  ::: *.in
