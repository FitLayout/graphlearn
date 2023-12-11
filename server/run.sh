#!/bin/sh

# Run the image
docker rm -f fitlayout-server || true && docker run -d -p 8400:8400 --mount 'type=bind,source=/opt/storage,target=/opt/storage' --mount 'type=bind,source=/home/burgetr/work/fitlayout/serve/config,target=/opt/config' --name fitlayout-server --restart unless-stopped fitlayout/fitlayout-server 
