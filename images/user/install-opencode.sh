#!/bin/bash
set -ex
OPENCODE_VERSION=v1.17.15
# hardcode env for Dockerfile
platform="linux-x64"
curl -s -L https://github.com/anomalyco/opencode/releases/download/${OPENCODE_VERSION}/opencode-${platform}.tar.gz | tar -xzv -C "$CONDA_PREFIX/bin"
test -f $CONDA_PREFIX/bin/opencode

BIOROUTER_VERSION=v1.87.1
curl -s -L https://github.com/BaranziniLab/biorouter/releases/download/${BIOROUTER_VERSION}/biorouter-headless-${platform}.tar.gz | tar -xzv --strip 1 -C "$CONDA_PREFIX" headless-${platform}/bin
test -f $CONDA_PREFIX/bin/biorouter
