#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Building Sims4-Saver for macOS..."

# Check if uv is available
if ! command -v uv &> /dev/null
then
    echo "Error: uv is not installed. Please install uv first."
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
uv sync

# Build the executable using PyInstaller
echo "Building executable..."
uv run pyinstaller sims-saver.spec

# Check if build was successful
if [ -d "dist/Sims4-Saver.app" ]; then
    echo ""
    echo "Build successful! Application created at: dist/Sims4-Saver.app"
    echo ""
    echo "You can now run the application or distribute it to other macOS machines."
else
    echo ""
    echo "Build failed. Please check the error messages above."
    exit 1
fi
