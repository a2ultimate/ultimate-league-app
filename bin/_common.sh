#!/bin/bash
here=`dirname ${BASH_SOURCE[0]}`
export ULTIMATE_ROOT="$($here/_root_path.sh)"
export ULTIMATE_SRC_ROOT="$ULTIMATE_ROOT/src"
export ULTIMATE_VIRTUALENV_ROOT="$ULTIMATE_ROOT/env"
