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
import decimal
from decimal import Decimal
import threading
from gcodefollower import GCodeFollower
import tkinter as tk
from tkinter import ttk

gcode = None


class ConfigurationFrame(ttk.Frame):
    def __init__(self, parent):
        global gcode
        gcode = GCodeFollower(echo_callback=self.echo,
                              enable_ui_callback=self.enableUI)
        gcode.saveDocumentationOnce()
        self.generateTimer = None
        self.templateGCodePath = tk.StringVar()
        self.temperatureVs = [tk.StringVar(), tk.StringVar()]
        self.statusV = tk.StringVar()
        ttk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH, expand=True)
        row = 0
        self.tgcLabel = ttk.Label(self, text="Template G-Code Path:")
        self.tgcLabel.grid(column=0, row=row, sticky=tk.E)
        self.tgcEntry = ttk.Entry(self, width=35,
                                  textvariable=self.templateGCodePath)
        self.tgcEntry.grid(column=1, columnspan=2, row=row, sticky=tk.E)
        row += 1
        self.minLabel = ttk.Label(self, text="Minimum Temperature (C):")
        self.minLabel.grid(column=0, row=row, sticky=tk.E)
        self.minEntry = ttk.Entry(self, width=35,
                                  textvariable=self.temperatureVs[0])
        self.minEntry.grid(column=1, columnspan=2, row=row, sticky=tk.E)
        row += 1
        self.maxLabel = ttk.Label(self, text="Maximum Temperature (C)")
        self.maxLabel.grid(column=0, row=row, sticky=tk.E)
        self.maxEntry = ttk.Entry(self, width=35,
                                  textvariable=self.temperatureVs[1])
        self.maxEntry.grid(column=1, columnspan=2, row=row, sticky=tk.E)
        row += 1
        ttk.Label(self, text="").grid(column=0, row=row, sticky=tk.E)
        # See Mitch McMabers' answer
        # at <https://stackoverflow.com/questions/4011354/\
        # create-resizable-multiline-tkinter-ttk-labels-with-word-wrap>
        # self.statusLabel = ttk.Label(self, width=25, wraplength=72,
        #                              anchor=tk.W, justify=tk.LEFT,
        #                              textvariable=self.statusV,
        #                              state="readonly")
        # self.statusLabel.grid(column=0, columnspan=3, row=row,
        #                       sticky=tk.E)
        self.statusLabel = ttk.Label(self, width=72, wraplength=600,
                                     anchor=tk.W,
                                     textvariable=self.statusV,
                                     state="readonly")
        self.statusLabel.grid(column=0, columnspan=3, row=row,
                              sticky=tk.W)
        row += 1
        self.generateButton = ttk.Button(self, text="Generate",
                                         command=self.generateTower)
        self.generateButton.grid(column=1, row=row, sticky=tk.E)
        self.exitButton = ttk.Button(self, text="Exit",
                                     command=root.destroy)
        self.exitButton.grid(column=2, row=row, sticky=tk.E)
        for child in self.winfo_children():
            child.grid_configure(padx=6, pady=3)
        # (Urban & Murach, 2016, p. 515)
        self.checkSettingsAndShow()
        self.pullSettings()  # Get the path even if temperature is bad.
        if not os.path.isfile(gcode._settingsPath):
            gcode.saveSettings()
        self.statusV.set("")

    def checkSettingsAndShow(self):
        try:
            return gcode.checkSettings()
            # Even if it returns True, don't save settings yet since
            # gcode.generateTower will do that.
        except ValueError:
            self.echo("The temperatures must be integers or Generate"
                      " cannot proceed.")
        except FileNotFoundError:
            # self.echo("")
            # checkSettings already called echo_callback in this case.
            pass
        return False

    def pushSettings(self):
        for i in range(2):
            gcode.setRangeVar("temperature", i,
                              self.temperatureVs[i].get())
        gcode.setVar("template_gcode_path",
                     self.templateGCodePath.get())

    def pullSettings(self):
        for i in range(2):
            v = gcode.getRangeVar("temperature", i)
            if v is not None:
                self.temperatureVs[i].set(v)
        # print("got template_gcode_path: "
        #       + gcode.getVar("template_gcode_path"))
        self.templateGCodePath.set(gcode.getVar("template_gcode_path"))

    def echo(self, msg):
        if len(msg) > 0:
            print("STATUS: " + msg)
            self.statusV.set(msg)
        else:
            print(msg)

    def enableUI(self, enable):
        if enable:
            self.generateButton.config(state=tk.NORMAL)
        else:
            self.generateButton.config(state=tk.DISABLED)

    def generateTower(self):
        self.pushSettings()
        gcode.enableUI(False)  # generateTower will call
        #                      # enable_ui_callback(true).
        # Start a thread, so that events related to enableUI(False) can
        # occur before processing.
        # gcode._verbose = True
        if self.checkSettingsAndShow():
            self.generateTimer = threading.Timer(0.01, gcode.generateTower)
            self.generateTimer.start()


def main():
    global root
    root = tk.Tk()
    root.title("Tower Configuration by Poikilos")
    ConfigurationFrame(root)
    root.mainloop()
    # (Urban & Murach, 2016, p. 515)


if __name__ == "__main__":
    main()

# References
# Urban, M., & Murach, J. (2016). Murach’s Python Programming
#     [VitalSource Bookshelf]. Retrieved from
#     https://bookshelf.vitalsource.com/#/books/9781943872152
