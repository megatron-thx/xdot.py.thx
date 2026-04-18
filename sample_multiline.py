#!/usr/bin/env python
#
# Copyright 2008 Jose Fonseca
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# megaton-thx multiline example
#
#gedit
#               command = "gedit "+ file_parts[1]+" +"+ line_parts[0]
#kate
#               command = "kate " + file_parts[1]+" -l"+ line_parts[0]
#

import os
import sys
import subprocess
import warnings

base = os.path.dirname(os.path.abspath(__file__))
graphviz_bin = os.path.join(base, "Graphviz", "Graphviz-14.1.4-win64", "bin")

if os.path.exists(graphviz_bin):
    os.environ["PATH"] = graphviz_bin + os.pathsep + os.environ.get("PATH", "")
    print(f"✅ Added Graphviz to PATH: {graphviz_bin}")
else:
    print(f"❌ Graphviz bin not found at: {graphviz_bin}")

import gi
gi.require_version('Gtk', '3.0')

# Silence common harmless warnings
warnings.filterwarnings("ignore", category=RuntimeWarning,
                        message=r".*Adding extra reference for.*Gtk.ToolItem.*")
warnings.filterwarnings("ignore", category=RuntimeWarning,
                        message=r".*couldn't load font.*Bitstream Vera.*")

from gi.repository import Gtk

import xdot.ui
from xdot.config import config

class MyDotWindow(xdot.ui.DotWindow):
    def __init__(self):
        xdot.ui.DotWindow.__init__(self)
        self.dotwidget.connect('clicked', self.on_url_clicked)

    def on_url_clicked(self, widget, url, event):
        if not url:
            return True

        print("Clicked URL:", url)

        if config.multi_line_activate and config.line_separator in url:
            urls = url.split(config.line_separator)
            for single_url in urls:
                self.open_in_vscode(single_url)
        else:
            self.open_in_vscode(url)

        return True

    def open_in_vscode(self, url):
        # Example: vscode://file/C:/path/to/file.py:42:10
        if url.startswith("vscode://file/"):
            try:
                path_args = url[16:]  # removes "vscode://file/"

                # ✅ Replace os.system() with this:
                if sys.platform == "win32":
                    subprocess.Popen(
                        ["code", "--goto", path_args],
                        creationflags=subprocess.CREATE_NO_WINDOW  # Hides cmd.exe
                    )
                else:
                    subprocess.Popen(["code", "--goto", path_args])

            except Exception as e:
                print(f"Failed to open in VSCode: {e}", file=sys.stderr)

    '''
    def on_url_clicked(self, widget, url, event):
        if url is not None:
            print(url)
            command = f'echo "url {url}"'
            if config.multi_line_activate:
                call_parts = url.split(":")
                if len(call_parts) > 1:
                    file_parts = call_parts[0].split("[")
                    line_parts = call_parts[1].split("]")

                    command = "echo url '"+ file_parts[1]+" +"+ line_parts[0]+ "'"

            to_run="%s" % command
            error = os.system(to_run)

        return True
    '''

def main():
    config.multi_line_activate = True

    window = MyDotWindow()
    base_dir = os.getcwd()
    #example_file = os.path.join(base_dir, "multiline_examples", "example_01.dot")
    #example_file = os.path.join(base_dir, "multiline_examples", "example_02.dot")
    #example_file = os.path.join(base_dir, "multiline_examples", "example_grok_01.dot")
    #example_file = os.path.join(base_dir, "multiline_examples", "example_grok_02.dot")
    #example_file = os.path.join(base_dir, "multiline_examples", "example_grok_03.dot")

    example_file = os.path.join(base_dir, "tests", "multiline_examples", "example_grok_05.dot")

    #example_file ="D:\\projects\\KaonMasterInquisitor\\output\\o01.dot"
    #example_file ="D:\\projects\\KaonMasterInquisitor\\output\\o02_xdot.dot"

    window.open_file(example_file)

    window.connect('delete-event', Gtk.main_quit)
    Gtk.main()

if __name__ == '__main__':
    main()

