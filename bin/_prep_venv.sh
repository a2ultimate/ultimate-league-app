#!/bin/bash
set -ex

here=`dirname ${BASH_SOURCE[0]}`
source "$here/_common.sh" $1

valid_modes="prod dev"
if [[ "$valid_modes" =~ "$1" ]]; then
	reqs="$1"
	venv="$1"
else
	echo "ERROR: No mode parameter provided. Expecting one of: $valid_modes"
	exit 1
fi

# Here's where the virtualenv ought to go
virtual_env=$ULTIMATE_VIRTUALENV_ROOT/$venv

# Optionally delete previously built virtualenv
if [ "x$2" == "xclean" ]; then
	if [ -d $virtual_env ]; then
		echo "Removing existing virtualenv"
	    rm -rf $virtual_env
	fi
fi

# Create virtualenv and install necessary packages
virtualenv --no-site-packages --prompt="(ulti $venv) " $virtual_env
. $virtual_env/bin/activate

pip install -r $ULTIMATE_SRC_ROOT/requirements/$reqs.txt
pip freeze > $ULTIMATE_SRC_ROOT/requirements/$reqs.full.txt
