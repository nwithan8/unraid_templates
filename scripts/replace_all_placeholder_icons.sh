#!/bin/sh

IMAGE_FOLDER="../images"
PLACEHOLDER_IMAGE="$IMAGE_FOLDER/placeholder-icon.png"

# DO NOT EDIT BELOW

# This is the MacOS equivalent command, will fail on Linux)
PLACEHOLDER_IMAGE_SIZE_BYTES=$(stat -c "%z" "$PLACEHOLDER_IMAGE")
FIND_RESULTS=$(find ../images/ -type f -size $PLACEHOLDER_IMAGE_SIZE_BYTES)

for file in $FIND_RESULTS; do
    cp "$PLACEHOLDER_IMAGE" "${file}"
    echo "Updated ${file}"
done;
