#!/bin/bash

set -e

hash pymongo-migrate 2>/dev/null || { echo >&2 "pymongo-migrate required, not installed."; exit 0; }

MIGRATIONS_DIR="migrations"
MIGRATIONS_COLLECTION="migrations"

if [ -z $MONGO_URI ]; then
    echo "Usage: MONGO_URI=<uri> migrate"
    exit 1
fi

pymongo-migrate migrate -u $MONGO_URI -m $MIGRATIONS_DIR -c $MIGRATIONS_COLLECTION