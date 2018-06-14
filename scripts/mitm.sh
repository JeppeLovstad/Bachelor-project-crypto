#!/bin/bash

python ../tcpproxy.py -ti 127.0.0.1 -tp 4433 -li 127.0.0.1 -lp 8200 -om client_module

$SHELL
