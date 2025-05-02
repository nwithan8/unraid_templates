#!/bin/sh

IMAGE_FOLDER="../images"
PLACEHOLDER_IMAGE="$IMAGE_FOLDER/placeholder-icon.png"

# DO NOT EDIT BELOW

# This is the MacOS equivalent command, will fail on Linux)
PLACEHOLDER_IMAGE_SIZE_BYTES=$(stat -f "%z" "$PLACEHOLDER_IMAGE")

echo "$PLACEHOLDER_IMAGE_SIZE_BYTES"

FIND_RESULTS=$(find $IMAGE_FOLDER -type f -size ${PLACEHOLDER_IMAGE_SIZE_BYTES}c)

echo "$FIND_RESULTS"

for file in $FIND_RESULTS; do
    cp "$PLACEHOLDER_IMAGE" "${file}"
    echo "Updated ${file}"
done;
