#!/bin/bash

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run the image
docker rm -f fitlayout-server || true && docker run -d -p 8400:8400 --mount 'type=bind,source=/opt/storage,target=/opt/storage' --mount "type=bind,source=$BASEDIR/config,target=/opt/config" --name fitlayout-server --restart unless-stopped fitlayout/fitlayout-server 
