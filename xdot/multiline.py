# xdot/multiline.py
#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import warnings
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Silence known harmless GTK warnings
warnings.filterwarnings("ignore", category=RuntimeWarning,
                        message=r".*Adding extra reference for.*Gtk.ToolItem.*")
warnings.filterwarnings("ignore", category=RuntimeWarning,
                        message=r".*couldn't load font.*Bitstream Vera.*")

from xdot.ui import DotWindow
from xdot.config import config

class MultilineDotWindow(DotWindow):
    def __init__(self):
        super().__init__()
        self.dotwidget.connect('clicked', self.on_url_clicked)

    def on_url_clicked(self, widget, url, event):
        if not url:
            return True
        print("Clicked URL:", url, file=sys.stderr)
        self._open_url(url)
        return True

    def _abs_url(self, url):
        abs_url = url

        path_with_pos = url[len("vscode://file/"):]

        # Split off line/column if present
        parts = path_with_pos.split(":")
        clean_path = ":".join(parts[:-2])

        file_path = clean_path

        suffix = ":".join(parts[-2:]) if len(parts) > 1 else ""

        # Resolve relative paths
        if not os.path.isabs(clean_path):
            file_path = os.path.abspath(clean_path)

        # Rebuild vscode://file URI
        abs_url = f"vscode://file/{file_path}"
        if suffix:
            abs_url += f":{suffix}"

        return abs_url

    def _open_url(self, url):
        if url.startswith("vscode://file/"):
            abs_url = self._abs_url(url)
            try:
                if sys.platform == "win32":
                    # ✅ Windows: let the OS handle the URI protocol
                    os.startfile(abs_url)
                else:
                    # Linux/macOS fallback: use xdg-open or open
                    import subprocess
                    opener = "xdg-open" if sys.platform.startswith("linux") else "open"
                    subprocess.Popen([opener, abs_url])

            except Exception as e:
                print(f"Failed to open in VSCode: {e}", file=sys.stderr)

def _setup_graphviz_path():
    """Optionally inject local Graphviz into PATH (useful for dev/CI)."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    graphviz_bin = os.path.join(base, "Graphviz", "Graphviz-14.1.4-win64", "bin")
    if os.path.exists(graphviz_bin):
        os.environ["PATH"] = graphviz_bin + os.pathsep + os.environ.get("PATH", "")
        print(f"✅ Added Graphviz to PATH: {graphviz_bin}", file=sys.stderr)
    elif not os.environ.get("PATH") or "graphviz" not in os.environ["PATH"].lower():
        print("⚠️ Graphviz not found in PATH. Ensure `dot` is accessible.", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Interactive multiline xdot viewer")
    parser.add_argument("dotfile", nargs="?", default=None, help="Path to the .dot file")
    parser.add_argument("--no-graphviz-setup", action="store_true",
                        help="Skip automatic local Graphviz PATH injection")
    args = parser.parse_args()

    if not args.no_graphviz_setup:
        _setup_graphviz_path()

    config.multi_line_activate = True

    window = MultilineDotWindow()
    if args.dotfile:
        if not os.path.exists(args.dotfile):
            print(f"Error: File not found: {args.dotfile}", file=sys.stderr)
            sys.exit(1)
        window.open_file(args.dotfile)

    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()