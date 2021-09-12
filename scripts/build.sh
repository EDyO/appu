#!/bin/bash

set -eu

mkdir -p build

OS=${1:-$(uname -s | tr -s '[A-Z]' '[a-z')}
ARCH=${2:-$(uname -m | sed -e 's/x86_/amd/g')}

for command in $(ls cmd); do
    GOOS=${OS} GOARCH=${ARCH} go build -o build/$command.${OS}_${ARCH} ./cmd/$command
done