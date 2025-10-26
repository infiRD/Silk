#! python
# -*- coding: utf-8 -*-
r"""Invocation script for working with FreeCAD from live REPL

Following code is tested with conda distribution of FreeCAD that properly sets
PYTHONPATH to allow loading the FreeCAD modules. Before running the code below
activate the conda env by:

  conda activate <env_name>

WINDOWS:
-------
There must be a file C:/Anaconda3/envs/<env_name>/etc/conda/activate.d/set_pythonpath.bat:

  @echo off
  set PYTHONPATH=%PYTHONPATH%;C:\Anaconda3\envs\<env_name>\Library\bin
  set PYTHONPATH=%PYTHONPATH%;C:\Anaconda3\envs\<env_name>\Library\lib

LINUX:
-----
TODO

Author:  Martin Zamba
Since:   October 2025
License: MIT
===============================================================================
"""

# spellchecker: ignore FREECAD Pixmaps Zamba ptpython

# %% ------------------------------------------------------------------------ #
# Run FreeCAD from python in separate thread with custom DPI scaling
# - python:          works
# - ipython:         FAILS - weird incompatibilities with event loop
# - ptpython:        works, with syntax highlight, but VEERY slow
# - FreeCAD 0.21.2:  ??
# - FreeCAD 1.1:     works
# --------- ----------------------------------------------------------------- #
import os  # noqa
import sys  # noqa
import threading  # noqa

import FreeCAD as App  # noqa
import FreeCADGui as Gui  # noqa

from PySide2.QtCore import QCoreApplication, Qt  # noqa
from PySide2.QtWidgets import QApplication  # noqa

os.environ["QT_SCALE_FACTOR"] = "0.75"
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# set configs location
os.environ["FREECAD_USER_HOME"] = os.path.join(os.environ["APPDATA"], "FreeCAD")


def start_gui():  # noqa # type: ignore
    Gui.showMainWindow()
    Gui.exec_loop()


gui_thread = threading.Thread(target=start_gui)
gui_thread.daemon = True
gui_thread.start()


# %% ------------------------------------------------------------------------ #
# Sample ops
# --------- ----------------------------------------------------------------- #
Gui.Selection.getSelection()
App.Console.PrintWarning("Warning message\n")
App.Console.PrintError("Error message\n")
App.Console.PrintLog("Log message\n")
