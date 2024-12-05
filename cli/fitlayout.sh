#!/bin/sh

# EDIT: Location of the artifact RDF storage
STORAGE_PATH="/opt/fitlayout/storage-cli"

# EDIT: Output folder location for storing the EXPORT command results
OUTPUT_FOLDER="$PWD"

# EDIT: An optional folder with browser extensions to be used for rendering
EXT_FOLDER="/opt/config/browser-extensions"

# If the FL_STORAGE environment variable is set, use it as the storage path
if [ -n "$FL_STORAGE" ]; then
    STORAGE_PATH="$FL_STORAGE"
fi

# Check the folders
if [ ! -d "$STORAGE_PATH" ]; then
        mkdir -p "$STORAGE_PATH"
fi
if [ ! -d "$OUTPUT_FOLDER" ]; then
        mkdir -p "$OUTPUT_FOLDER"
fi

echo "Local storage is mapped to $STORAGE_PATH"

# Mount the extensions folder if present
EXT=""
if [ -d "$EXT_FOLDER" ]; then
	EXT="--mount type=bind,source=$EXT_FOLDER,target=/opt/fitlayout-puppeteer/extensions"
fi

# Run the image
docker run --rm \
  --mount type=bind,source="$STORAGE_PATH",target=/opt/storage/storage-cli \
  --mount type=bind,source="$OUTPUT_FOLDER",target=/out $EXT \
  fitlayout/fitlayout-cli $@
