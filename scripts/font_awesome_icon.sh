#!/usr/bin/env bash

# Use a Font Awesome icon as a template logo

# Usage: ./font_awesome_icon.sh <icon_name> <app_name>

ICON_NAME=$1
APP_NAME=$2
ICON_SECTION=${3:-solid}

if [ -z "$ICON_NAME" ] || [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <icon_name> <app_name>"
  exit 1
fi

# Replace any spaces in the app name with dashes
APP_NAME=${APP_NAME// /-}

TMP_FILE="tmp_icon.svg"

# Download the icon from Font Awesome
echo "Downloading icon: $ICON_NAME"
wget --no-check-certificate -q -O "$TMP_FILE" "https://site-assets.fontawesome.com/releases/v6.7.2/svgs/${ICON_SECTION}/${ICON_NAME}.svg"

if [ $? -ne 0 ]; then
  echo "Failed to download icon: $ICON_NAME"
  exit 1
fi

# Convert the SVG to PNG using cairosvg
cairosvg "$TMP_FILE" -f png -o "images/${APP_NAME}-icon.png"

# Check if the conversion was successful
if [ $? -ne 0 ]; then
  echo "Failed to convert SVG to PNG"
  rm "$TMP_FILE"
  exit 1
fi

# Clean up the temporary file
rm "$TMP_FILE" || true
# rm "wget-log" || true
