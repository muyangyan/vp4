#!/bin/bash
# Script to install PRISM model checker

set -e

echo "================================================"
echo "PRISM Model Checker Installation"
echo "================================================"
echo ""

PRISM_VERSION="4.8.1"
PRISM_DIR="prism-${PRISM_VERSION}-linux64-x86"
PRISM_ARCHIVE="${PRISM_DIR}.tar.gz"
INSTALL_DIR="$HOME/prism"

echo "Installing PRISM ${PRISM_VERSION}..."
echo ""

# Create installation directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download PRISM
if [ ! -f "$PRISM_ARCHIVE" ]; then
    echo "Downloading PRISM ${PRISM_VERSION}..."
    wget "https://github.com/prismmodelchecker/prism/releases/download/v${PRISM_VERSION}/${PRISM_ARCHIVE}"
else
    echo "Archive already exists, skipping download..."
fi

# Extract
if [ ! -d "$PRISM_DIR" ]; then
    echo "Extracting archive..."
    tar -xzf "$PRISM_ARCHIVE"
else
    echo "PRISM already extracted..."
fi

echo ""
echo "================================================"
echo "Installation Complete!"
echo "================================================"
echo ""
echo "PRISM is installed in: $INSTALL_DIR/$PRISM_DIR"
echo ""
echo "To use PRISM, add it to your PATH:"
echo ""
echo "  export PATH=\$PATH:$INSTALL_DIR/$PRISM_DIR/bin"
echo ""
echo "Add this line to your ~/.bashrc or ~/.profile to make it permanent:"
echo ""
echo "  echo 'export PATH=\$PATH:$INSTALL_DIR/$PRISM_DIR/bin' >> ~/.bashrc"
echo "  source ~/.bashrc"
echo ""
echo "Test the installation with:"
echo "  prism -version"
echo ""

# Test if Java is available
if ! command -v java &> /dev/null; then
    echo "WARNING: Java is not installed!"
    echo "PRISM requires Java to run. Install it with:"
    echo "  sudo apt-get install default-jre"
    echo ""
fi

