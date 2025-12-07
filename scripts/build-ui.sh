#!/bin/bash

# UI Shell Build & Dev Script

echo "SERP UI Shell - Build & Development"
echo "====================================="

UI_SHELL_PATH="$(dirname "$0")/../ui-shell"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Check Node version
NODE_VERSION=$(node --version)
echo "Node.js version: $NODE_VERSION"

# Navigate to ui-shell
cd "$UI_SHELL_PATH"

echo ""
echo "Installing dependencies..."
npm install

echo ""
echo "Running type check..."
npm run type-check

echo ""
echo "Running linter..."
npm run lint

echo ""
echo "Build complete!"
echo ""
echo "To start development server:"
echo "  cd ui-shell"
echo "  npm run dev"
echo ""
echo "To build for production:"
echo "  cd ui-shell"
echo "  npm run build"
