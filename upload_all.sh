#!/bin/bash
# upload_all.sh - Build and upload all packages (default_packages + root) to PyPI

# Exit on any error
set -e

# Ensure we are in the project root
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$ROOT_DIR"

# Path to venv binaries
PYTHON="$ROOT_DIR/venv/bin/python"
TWINE="$ROOT_DIR/venv/bin/twine"

# Safety check for venv and twine
if [ ! -f "$PYTHON" ] || [ ! -f "$TWINE" ]; then
    echo "❌ Error: Virtual environment or twine not found in ./venv"
    exit 1
fi

# Create a clean unified dist directory
FINAL_DIST="$ROOT_DIR/all_dist"
rm -rf "$FINAL_DIST"
mkdir -p "$FINAL_DIST"

echo "📦 Building all packages..."
echo "--------------------------"

# List of all package directories to build (default_packages + root)
PACKAGES=(".")
for d in default_packages/*; do
    if [ -d "$d" ]; then
        PACKAGES+=("$d")
    fi
done

for pkg in "${PACKAGES[@]}"; do
    # Check if it's a valid python package
    if [ -f "$pkg/pyproject.toml" ] || [ -f "$pkg/setup.py" ]; then
        pkg_name=$(basename "$pkg")
        if [ "$pkg" == "." ]; then pkg_name="shopyo (root)"; fi

        echo "🛠️  Building: $pkg_name"

        # Subshell to build and output directly to our unified dist folder
        (
            cd "$pkg"
            # Clean local build artifacts
            rm -rf dist/ build/ *.egg-info
            # Build using the modern 'build' module
            "$PYTHON" -m build --outdir "$FINAL_DIST" . > /dev/null
        )
    fi
done

echo ""
echo "🚀 Uploading to PyPI..."
echo "--------------------------"
echo "Twine will prompt for credentials once for the entire batch."
echo "Using --skip-existing to avoid errors for already uploaded versions."
echo ""

# Upload all files in the unified dist directory
# --skip-existing prevents failures if a version already exists on PyPI
"$TWINE" upload --skip-existing "$FINAL_DIST"/*

# Cleanup
rm -rf "$FINAL_DIST"

echo ""
echo "✅ All packages processed successfully!"
