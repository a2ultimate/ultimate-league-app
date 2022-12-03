#!/bin/bash
set -e

here=`dirname ${BASH_SOURCE[0]}`
root=`cd -P "$here/../" && pwd`

BIN_ROOT="$here"
SRC_ROOT="$root/src"
VENV_ROOT="$root/venv"

valid_modes="prod dev"
if [[ "$valid_modes" =~ "$1" ]]; then
  mode="$1"
else
  echo "ERROR: No mode parameter provided. Expecting one of: $valid_modes"
  exit 1
fi

# Here's where the virtualenv ought to go
virtual_env=$VENV_ROOT/$mode

# Optionally delete previously built virtualenv
if [ "x$2" == "xclean" ]; then
  if [ -d "$virtual_env" ]; then
  echo "Removing existing virtualenv"
      rm -rf "$virtual_env"
  fi
fi

# Create virtualenv and install necessary packages
virtualenv --python="$(which python3)" --prompt="(ulti $mode) " "$virtual_env"
. "$virtual_env/bin/activate"

pip install --no-cache-dir -r $SRC_ROOT/requirements/$mode.txt
pip freeze > $SRC_ROOT/requirements/$mode.full.txt
