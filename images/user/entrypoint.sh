#!/usr/bin/bash -l
export CONDA_ROOT=/srv/.pixi/envs/default
export MAMBA_ROOT_PREFIX=$CONDA_ROOT
source $CONDA_ROOT/etc/profile.d/mamba.sh
mamba activate $CONDA_ROOT
exec tini -- "$@"
