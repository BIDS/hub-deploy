#!/usr/bin/bash -l
set -e
mamba activate $MAMBA_ROOT_PREFIX
exec "$@"
