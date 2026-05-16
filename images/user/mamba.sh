# activate default env in login shells
eval "$($MAMBA_ROOT_PREFIX/bin/mamba shell hook)"
mamba activate $MAMBA_ROOT_PREFIX
