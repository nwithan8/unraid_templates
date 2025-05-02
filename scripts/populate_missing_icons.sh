#!/usr/bin/env bash

ICON_DIR="images"
TEMPLATE_ICON_DIR="templates"
TEMP_ICON=$ICON_DIR/"placeholder-icon.png"

# For each template in the template directory, check if the icon exists in the icon directory
for template in "$TEMPLATE_ICON_DIR"/*; do
    # Get the base name of the template (without the directory)
    app_name=$(basename "$template")

    # Remove the .xml extension to get the base name
    app_name="${app_name%.xml}"

    # Replace underscores with dashes
    app_name="${app_name//_/-}"

    # Construct the corresponding icon file name
    icon_file="$ICON_DIR/${app_name}-icon.png"

    # Check if the icon file exists
    if [ ! -f "$icon_file" ]; then
        echo "$icon_file for $app_name not found. Copying placeholder."
        cp "$TEMP_ICON" "$icon_file"
    else
        echo "Icon for $app_name already exists."
    fi
done
