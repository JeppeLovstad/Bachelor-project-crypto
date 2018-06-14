#!/bin/bash

openssl s_server -key key.pem -cert cert.pem -cipher DES-CBC3-SHA -quiet

$SHELL
