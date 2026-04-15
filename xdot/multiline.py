# xdot/multiline.py
#!/usr/bin/env python3
import os
import sys
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
        if config.multi_line_activate and config.line_separator in url:
            for single_url in url.split(config.line_separator):
                self._open_url(single_url)
        else:
            self._open_url(url)
        return True

    def _open_url(self, url):
        if url.startswith("vscode://file/"):
            try:
                # Remove "vscode://file/" prefix -> "C:/path/to/file.py:42:10"
                path_args = url[16:]
                os.system(f'code --goto "{path_args}"')
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