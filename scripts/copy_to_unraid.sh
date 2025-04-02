#!/usr/bin/env bash

# Copy template to Unraid

TEMPLATE_PATH=$1

if [ -z "$TEMPLATE_PATH" ]; then
  echo "Usage: $0 <template_path>"
  exit 1
fi

scp -r "$TEMPLATE_PATH" bigbox:/boot/config/plugins/dockerMan/templates/nwithan8/
