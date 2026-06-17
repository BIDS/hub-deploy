# activate default env in login shells
eval "$($MAMBA_ROOT_PREFIX/bin/mamba shell hook -s bash)"
mamba activate $MAMBA_ROOT_PREFIX
