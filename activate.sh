#!/usr/bin/env bash

# Activate the virtual environment (Windows venv layout)
source .venv/Scripts/activate

# Base directory is wherever you run this script
BASE_DIR="$(pwd)"

# Add GTK bin to PATH
export PATH="$BASE_DIR/gtk/bin:$PATH"

# Add GTK pkg-config path
export PKG_CONFIG_PATH="$BASE_DIR/gtk/lib/pkgconfig:$PKG_CONFIG_PATH"

# Add Graphviz bin to PATH
export PATH="$BASE_DIR/Graphviz/Graphviz-14.1.4-win64/bin:$PATH"

echo "Project environment activated with GTK + Graphviz paths"
