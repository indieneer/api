#!/bin/bash

set -e

hash pymongo-migrate 2>/dev/null || { echo >&2 "pymongo-migrate required, not installed."; exit 0; }

MIGRATIONS_DIR="migrations"

if [ -z $1]; then
    echo "Usage: create-migration [NAME]"
    exit 1
fi

pymongo-migrate generate -m $MIGRATIONS_DIR "$(date +%s%N | cut -b1-13)_$1"