#!/bin/bash

FILES="./virt-player"
FILES="${FILES} $(find ./lib -name '*.py' | tr '\n' ' ')"

autopep8 -ia --ignore=E402,E501 ${FILES}
