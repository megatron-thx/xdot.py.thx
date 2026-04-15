#!/usr/bin/env bash
set -euo pipefail

# 🔍 Robust Python 3 Detection (Git Bash / Windows / Linux)
detect_python() {
    for cmd in python3 python py python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            "$cmd" -c "import sys; exit(0 if sys.version_info[0]==3 else 1)" && {
                echo "$cmd"
                return 0
            }
        fi
    done
    return 1
}

PY=$(detect_python) || {
    echo "❌ Python 3 not found in PATH."
    echo "💡 Fix: Ensure Python is installed and 'python' or 'py' is in your system PATH."
    echo "   Debug: Run 'echo \$PATH' to verify."
    exit 1
}

echo "🐍 Detected Python: $($PY --version 2>&1) => Using command: $PY"

BASE_DIR="$(pwd)"
VENV_DIR="$BASE_DIR/.venv"
DOWNLOADS_DIR="$VENV_DIR/downloads"
GTK_DIR="$VENV_DIR/gtk"
GV_DIR="$VENV_DIR/Graphviz"

GTK_ZIP="GTK3_Gvsbuild_2026.3.0_x64.zip"
GTK_URL="https://github.com/wingtk/gvsbuild/releases/download/2026.3.0/$GTK_ZIP"
GV_ZIP="windows_10_cmake_Release_Graphviz-14.1.4-win64.zip"
GV_URL="https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/14.1.4/$GV_ZIP"

echo "🔧 Bootstrapping isolated xdot environment in .venv/..."

# 1️⃣ Create venv (idempotent)
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating Python virtual environment..."
    $PY -m venv "$VENV_DIR"
fi

# Activate & upgrade pip
source "$VENV_DIR/Scripts/activate"
$PY -m pip install --upgrade pip > /dev/null 2>&1

# 2️⃣ Ensure subdirectories exist
mkdir -p "$DOWNLOADS_DIR" "$GTK_DIR" "$GV_DIR"

# 3️⃣ GTK3 Setup
if [ ! -d "$GTK_DIR/bin" ]; then
    echo "⬇️  Downloading GTK3..."
    curl -fSL "$GTK_URL" -o "$DOWNLOADS_DIR/$GTK_ZIP"
    unzip -q "$DOWNLOADS_DIR/$GTK_ZIP" -d "$GTK_DIR"
    rm -f "$DOWNLOADS_DIR/$GTK_ZIP"
else
    echo "✅ GTK3 already extracted."
fi

# 4️⃣ Graphviz Setup
if [ ! -d "$GV_DIR" ] || [ -z "$(ls -A "$GV_DIR" 2>/dev/null)" ]; then
    echo "⬇️  Downloading Graphviz..."
    curl -fSL "$GV_URL" -o "$DOWNLOADS_DIR/$GV_ZIP"
    unzip -q "$DOWNLOADS_DIR/$GV_ZIP" -d "$GV_DIR"
    #rm -f "$DOWNLOADS_DIR/$GV_ZIP"
else
    echo "✅ Graphviz already extracted."
fi

# 5️⃣ Install wheels & Python deps
echo "📦 Installing local wheels & packages..."
$PY -m pip install --force-reinstall --no-deps "$GTK_DIR/wheels/pycairo-"*.whl
$PY -m pip install --force-reinstall --no-deps "$GTK_DIR/wheels/pygobject-"*.whl
$PY -m pip install numpy packaging

# 6️⃣ Install xdot.py in editable mode
echo "📦 Installing xdot.py (editable)..."
$PY -m pip install -e "$BASE_DIR" > /dev/null 2>&1

mkdir -p .venv/Lib/site-packages
cat > .venv/Lib/site-packages/sitecustomize.py << 'EOF'
import os, sys
def _setup():
    if sys.platform != "win32" or not hasattr(os, "add_dll_directory"): return
    root = sys.prefix
    for p in (os.path.join(root, "gtk", "bin"),):
        if os.path.isdir(p):
            try: os.add_dll_directory(p); os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")
            except: pass
    gv = os.path.join(root, "Graphviz")
    if os.path.isdir(gv):
        for d in os.listdir(gv):
            if d.startswith("Graphviz-"):
                bp = os.path.join(gv, d, "bin")
                if os.path.isdir(bp):
                    try: os.add_dll_directory(bp); os.environ["PATH"] = bp + os.pathsep + os.environ.get("PATH", "")
                    except: pass
_setup()
EOF
echo "✅ sitecustomize.py created"

echo ""
echo "🎉 Environment ready! Everything isolated in .venv/"
