#!/bin/bash
# Build all packages in the workspace

set -e

echo "Building SERP workspace packages..."

# Build core packages first (order matters due to dependencies)
echo "Building serp-core..."
cd packages/serp-core
uv build
cd ../..

echo "Building serp-shell..."
cd packages/serp-shell
uv build
cd ../..

echo "Building serp-cli..."
cd packages/serp-cli
uv build
cd ../..

# Build official modules
echo "Building serp-users..."
cd modules/serp-users
uv build
cd ../..

echo "Building serp-crm..."
cd modules/serp-crm
uv build
cd ../..

echo "Building serp-invoicing..."
cd modules/serp-invoicing
uv build
cd ../..

echo "✓ All packages built successfully!"
echo "Build artifacts are in each package's dist/ directory"
