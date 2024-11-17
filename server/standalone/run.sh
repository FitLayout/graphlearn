#!/usr/bin/env bash

# EDIT: Default location of the artifact RDF storage. It can be also
# overriden by setting the FL_STORAGE environment variable or by giving
# the path as the first argument of the script.
STORAGE_PATH="$HOME/.fitlayout/storage"

# If the storage path is given as an argument, use it
if [ ! $# -eq 0 ]; then 
    STORAGE_PATH="$1"
# or when the FL_STORAGE variable is set, use its value
elif [ -n "$FL_STORAGE" ]; then
    STORAGE_PATH="$FL_STORAGE"
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Run the image
docker rm -f fitlayout-server || true && docker run -d -p 8400:8400 --mount type=bind,source="$STORAGE_PATH",target=/opt/storage --mount type=bind,source="$SCRIPT_DIR/config",target=/opt/config --name fitlayout-server --restart unless-stopped fitlayout/fitlayout-server 
