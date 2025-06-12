#!/bin/sh

PLACEHOLDER_IMAGE="../images/placeholder-icon.png"
PLACEHOLDER_IMAGE_SIZE_BYTES=$(stat -f%z "$PLACEHOLDER_IMAGE")

FIND_RESULTS=$(find ../images/ -type f -size "$PLACEHOLDER_IMAGE_SIZE_BYTES"c)

for file in $FIND_RESULTS; do
    result=$(compare -metric AE "${file}" "$PLACEHOLDER_IMAGE" /tmp/diff.png 2>&1);
    if [ "${result}" != '0 (0)' ]; then
        echo "${file} is NOT the same as $PLACEHOLDER_IMAGE";
    else
	      echo "${file} passed";
    fi;
done;
