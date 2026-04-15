import os
import sys

def _inject_local_paths():
    """Inject .venv GTK/Graphviz paths BEFORE loading any C extensions."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv = os.path.join(base, ".venv")

    gtk_bin = os.path.join(venv, "gtk", "bin")

    # Dynamically find Graphviz-*/bin (version-agnostic)
    gv_base = os.path.join(venv, "Graphviz")
    gv_bin = None
    if os.path.isdir(gv_base):
        for d in os.listdir(gv_base):
            if d.startswith("Graphviz-") and os.path.isdir(os.path.join(gv_base, d)):
                gv_bin = os.path.join(gv_base, d, "bin")
                break

    dirs = [p for p in (gtk_bin, gv_bin) if p and os.path.isdir(p)]
    if not dirs:
        return  # Fallback to system PATH

    # Prepend to PATH so Windows finds DLLs first
    os.environ["PATH"] = os.pathsep.join(dirs) + os.pathsep + os.environ.get("PATH", "")

    # Python 3.8+ Windows DLL loader (bypasses PATH limitations)
    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        for d in dirs:
            try:
                os.add_dll_directory(d)
            except Exception:
                pass

# ⚠️ CRITICAL: Run path injection BEFORE importing gi/GTK
_inject_local_paths()

# Now it's safe to import GUI libraries
from xdot.multiline import main as run_multiline

def main():
    """Entry point for xdot-multiline CLI/GUI."""
    run_multiline()

if __name__ == "__main__":
    main()