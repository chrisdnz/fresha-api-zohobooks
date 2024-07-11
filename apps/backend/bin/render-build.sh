#!/usr/bin/env bash

# Exit on error
set -o errexit

npm install

# Install required Python packages
npx nx run backend:install

# Generate Prisma client
npx nx run backend:prisma

# Store/pull Prisma cache with build cache
if [[ ! -d $PRISMA_BINARY_CACHE_DIR ]]; then
    echo "...Copying Prisma Binary Cache from Build Cache"
    cp -R $XDG_CACHE_HOME/prisma/binaries $PRISMA_BINARY_CACHE_DIR
else
    echo "...Storing Prisma Binary Cache in Build Cache"
    cp -R $PRISMA_BINARY_CACHE_DIR $XDG_CACHE_HOME
fi
