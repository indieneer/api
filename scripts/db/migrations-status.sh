#!/bin/bash

set -e

hash pymongo-migrate 2>/dev/null || { echo >&2 "pymongo-migrate required, not installed."; exit 0; }

MIGRATIONS_DIR="migrations"
MIGRATIONS_COLLECTION="migrations"

if [ -z $MONGO_URI ]; then
    echo "Usage: MONGO_URI=<uri> migration-status"
    exit 1
fi

MIGRATIONS_STATUS=$(pymongo-migrate show -u $MONGO_URI -m $MIGRATIONS_DIR -c $MIGRATIONS_COLLECTION)
echo $MIGRATIONS_STATUS

if [[ $MIGRATIONS_STATUS == *"Not applied"* ]]; then
    echo "Warning: there are pending migrations"
    exit 1
fi