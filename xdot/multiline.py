# xdot/multiline.py
#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import warnings
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

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

def _set_dark_theme():
   # 🔒 SAFE DARK MODE INITIALIZATION
    settings = Gtk.Settings.get_default()
    if settings:
        try:
            settings.props.gtk_application_prefer_dark_variant = True
        except (TypeError, AttributeError):
            pass  # Property not available in this GTK build; CSS will handle it

    css_provider = Gtk.CssProvider()

    css_provider.load_from_data(b"""
        /* Remove all borders from window and titlebar */
        window {
            background: #1e1e1e;
            background-color: #1e1e1e;
        }

        .titlebar, headerbar {
            background: #1e1e1e;
            background-color: #1e1e1e;
            background-image: none;
            border: none;
            border-bottom: none;
            box-shadow: none;
            color: #e0e0e0;
        }

        .titlebar:backdrop, headerbar:backdrop {
            background: #1e1e1e;
            background-color: #1e1e1e;
            background-image: none;
            border: none;
        }

        /* Remove any separators or borders in toolbar */
        toolbar {
            background: #1e1e1e;
            background-color: #1e1e1e;
            border: none;
            box-shadow: none;
        }

        /* Target any remaining borders */
        .titlebar separator, headerbar separator,
        toolbar separator {
            background: #333333;
        }

        toolbar {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border-bottom: 1px solid #333;
        }
        menu, .menu, .popup {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #444;
        }
        menuitem, .menuitem {
            background-color: transparent;
            color: #e0e0e0;
        }
        menuitem:hover, .menuitem:hover {
            background-color: #3a3a3a;
        }
        entry, .entry {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #555;
        }
        tooltip {
            background-color: #333;
            color: #eee;
            border: 1px solid #555;
        }
    """)

    # Apply CSS to the default display (GTK 3.10+) with fallback for older builds
    """
    display = Gdk.Display.get_default()
    if display:
        Gtk.StyleContext.add_provider_for_display(display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    else:
    """
    if True:
        screen = Gdk.Screen.get_default()
        if screen:
            Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def main():
    parser = argparse.ArgumentParser(description="Interactive multiline xdot viewer")
    parser.add_argument("dotfile", nargs="?", default=None, help="Path to the .dot file")
    parser.add_argument("--no-graphviz-setup", action="store_true",
                        help="Skip automatic local Graphviz PATH injection")
    args = parser.parse_args()

    if not args.no_graphviz_setup:
        _setup_graphviz_path()

    config.multi_line_activate = True
    config.dark_theme = True

    if config.dark_theme:
        _set_dark_theme()

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