#!/usr/bin/env python3

# This program changes and inserts temperatures into gcode that builds a
# temperature tower.
# Copyright (C) 2019  Jake Gustafson

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import threading
from gcodefollower import GCodeFollower
# import tk_cli_dummy as tk  # This is for synchronizing code between
#                            # CLI and non-CLI versions.

gcode = None


def usage():
    print(GCodeFollower.getDocumentation())
    if gcode is not None:
        gcode.printSettingsDocumentation()
    print("")
    print("Command Line Usage:")
    print("  Examples:")
    print("  " + sys.argv[0] + " 190 210")
    # print(sys.argv[0] + " tower.gcode")
    print("  " + sys.argv[0] + " tower.gcode 190 210")
    print("")


class Application():
    def __init__(self):
        global gcode
        gcode = GCodeFollower(echo_callback=self.echo,
                              enable_ui_callback=self.enableUI)
        gcode.saveDocumentationOnce()
        self.generateTimer = None
        try:
            # usage()  # for debug only
            gcode.checkSettings(
                allow_previous_settings=False
                # verbose=False
            )  # This checks the sys.argv list too.
            # - Leave verbose=False since the errors are below in a form
            #   that is helpful for CLI operation.
            # - Even if it returns True, don't save settings yet, since
            #   gcode.generateTower will do that.
        except ValueError:
            usage()
            print("")
            print("ERROR:")
            print("- You must specify the temperature range.")
            if not os.path.isfile(gcode._settingsPath):
                gcode.saveSettings()
            exit(1)
        except FileNotFoundError:
            # self.echo("")
            # checkSettings already called echo_callback in this case.
            print("")
            print("ERROR:")
            print("'{}' does not"
                  " exist.".format(gcode.getVar("template_gcode_path")))
            tgp = gcode.getVar("template_gcode_path")
            tn = GCodeFollower._towerName
            if tgp == gcode.getVar("default_path"):
                print("You must first slice {}:".format(tn))
                for thisURL in gcode._downloadPageURLs:
                    print("  {}".format(thisURL))
            print("")
            if not os.path.isfile(gcode._settingsPath):
                gcode.saveSettings()
            exit(1)
        self.generateTower()

    def enableUI(self, enable):
        if enable:
            if len(gcode.stats) > 0:
                print("The process completed.")
                print("")
                print("Stats:")
                for k, v in gcode.stats.items():
                    print("  {}: {}".format(k, v))
        else:
            print("please wait...")

    def echo(self, msg):
        print(msg)

    def generateTower(self):
        gcode.enableUI(False)  # generateTower will call
        #                      # enable_ui_callback(true).
        # Start a thread, so that events related to enableUI(False) can
        # occur before processing.
        self.generateTimer = threading.Timer(0.01, gcode.generateTower)
        self.generateTimer.start()


def main():
    print("Welcome to Tower Configuration by Poikilos.")
    print("")
    Application()


if __name__ == "__main__":
    main()

# References
# Urban, M., & Murach, J. (2016). Murach’s Python Programming
#     [VitalSource Bookshelf]. Retrieved from
#     https://bookshelf.vitalsource.com/#/books/9781943872152
