# -*- coding: utf-8 -*-
r"""
ToolTipDialog.py - A tooltips dialog with zoom and scroll support
"""
#    This file is part of Silk
#
#    NURBS Surface modeling tools focused on low degree and seam continuity
#    (FreeCAD Workbench)
#
#    Silk is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Author:  Martin Zamba <martin.zamba@gmail.com>
# Since:   October 2025
# License: GNU GPL v3 or later

# spellchecker: ignore NURBS Zamba pylance consolas verdana zoomable

# Following try / except block is here to allow the code to work in qt6 / PySide6 (like 1.1.dev)
# and qt5 / PySide2 (like 0.21.2) based FreeCAD + it satisfies pylance in VSCode at the same time
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QWheelEvent
except Exception:
    from PySide import QtCore, QtGui, QtWidgets  # type: ignore
    from PySide.QtGui import QWheelEvent  # type: ignore

import math
from typing import Optional


class ToolTipWindow(QtWidgets.QDialog):  # type: ignore
    DEFAULT_FONT_SIZE: int = 12
    FONT_ZOOM_FACTOR: float = 1.2
    PREFERRED_FONT_NAME: str = "DejaVu Sans Mono"
    DEBUG = False
    DEFAULT_WIDTH = 1000
    MIN_WIDTH = 400
    MAX_COVER_X = 0.9
    MAX_COVER_Y = 0.8
    PADDING = 20

    text_edit: QtWidgets.QTextEdit
    tooltip: str

    def __init__(self, label: str, tooltip: str, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowType.Popup)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        self.setWindowTitle(label)

        screen_rect: QtCore.QRect = self.screen().availableGeometry()
        max_screen_height: int = math.ceil(screen_rect.height() * self.MAX_COVER_Y)
        self.resize(self.DEFAULT_WIDTH, max_screen_height)

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setReadOnly(True)

        self.tooltip = tooltip
        self.text_edit.setText(self.tooltip)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.text_edit)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        """Called just before the widget is shown"""

        self.print_debug_font_info()

        # Recreate and set the font to allow zoom in / out functionality
        # - I don't know why is this necessary, but if this is not done then
        #   text_edit.font().pointSize() or text_edit.font().pointSizeF() will
        #   always return -1 and text_edit.zoomIn() and text_edit.zoomOut() are
        #   just ignored
        # - this is probably due to FreeCAD setting the styles according to
        #   stylesheets

        # This should return the font being currently used to actually render
        # the QTextEdit
        font_name = self.text_edit.font().family()

        font_size = self.text_edit.font().pointSizeF()
        if font_size < 0:
            font_size = estimate_font_size(self.text_edit)

        # Try to set preferred font, if available on the system
        available_fonts = QtGui.QFontDatabase().families()
        if self.PREFERRED_FONT_NAME.lower() in (family.lower() for family in available_fonts):
            font_name = self.PREFERRED_FONT_NAME

        font = QtGui.QFont(font_name)
        font.setPointSizeF(font_size)
        self.text_edit.setFont(font)

        self.print_debug_font_info()

        self.update_size()
        self.center_on_screen()
        self.text_edit.setFocus()

        # Call the parent's showEvent to actually show the dialog
        super().showEvent(event)

    def update_size(self) -> None:
        """Will recalculate and set the dialog size"""
        dyn_w = self.calculate_dynamic_width()
        if self.DEBUG:
            print(f"{dyn_w=}")
        self.resize(dyn_w, self.height())

    def center_on_screen(self) -> None:
        """Will center the dialog on the screen"""
        frame_geom = self.frameGeometry()
        screen: QtGui.QScreen = self.screen()
        center_point = screen.availableGeometry().center()
        frame_geom.moveCenter(center_point)
        self.move(frame_geom.topLeft())

    def calculate_dynamic_width(self) -> int:
        """Determine dialog width based on displayed text given the set font"""

        screen: QtGui.QScreen = self.screen()
        if not screen:
            return self.DEFAULT_WIDTH

        screen_rect: QtCore.QRect = screen.availableGeometry()
        screen_width: int = screen_rect.width()
        max_screen_width: int = math.ceil(screen_width * self.MAX_COVER_X)

        metrics: QtGui.QFontMetrics = self.text_edit.fontMetrics()

        longest_line_width: int = 0
        for line in self.tooltip.split("\n"):
            # horizontalAdvance is preferred over width for modern Qt/font handling
            width_in_pixels: int = metrics.horizontalAdvance(line)
            if width_in_pixels > longest_line_width:
                longest_line_width = width_in_pixels

        padding_pixels: int = self.PADDING * 2
        required_text_width: int = longest_line_width + padding_pixels

        final_width: int = min(required_text_width, max_screen_width)
        return max(final_width, self.MIN_WIDTH)

    def print_debug_font_info(self) -> None:
        if self.DEBUG:
            font = self.text_edit.font()
            fm = self.text_edit.fontMetrics()

            print("FONT INFO:")
            print(f"{font.family()=}")
            print(f"{font.pointSize()=}")
            print(f"{font.pointSizeF()=}")
            print(f"{font.fixedPitch()=}")
            print(f"{fm.fontDpi()=}")
            print(f"{fm.height()=}")
            print(f"{fm.xHeight()=}")
            print(f"{fm.lineSpacing()=}")
            print(f"{fm.ascent()=}")
            print(f"{fm.descent()=}")
            print(f"{fm.leading()=}")
            print(f"{fm.capHeight()=}")

            computed_font_size = estimate_font_size(self.text_edit)
            print(f"{computed_font_size=}")

    def wheelEvent(self, event: QWheelEvent) -> None:
        modifiers: QtCore.Qt.KeyboardModifier = event.modifiers()

        if modifiers == QtCore.Qt.KeyboardModifier.ControlModifier:
            delta: int = event.angleDelta().y()
            if delta > 0:
                self.text_edit.zoomIn()
            else:
                self.text_edit.zoomOut()

            self.update_size()
            self.center_on_screen()

            # consume event
            event.accept()
        else:
            super().wheelEvent(event)

        self.print_debug_font_info()


def estimate_font_size(widget: QtWidgets.QWidget) -> float:
    """Try to estimate the font size from its metrics.

    This is inherently just approximate and may give different results depending on
    font design. For example for fixed width fonts like Courier New and Consolas, this
    will compute accurate or almost accurate size. However for fonts like Arial and
    Verdana the result may differ by ~15 %. For those fonts fontMetrics().ascent() if
    used instead of fontMetrics().height() would give better results

    AFAIK there is no reliable method to compute the font size from its metrics
    """
    font_height = widget.fontMetrics().height()
    dpi = widget.logicalDpiY()
    font_size = font_height * 72.0 / dpi
    return font_size


def tipsDialog(label: str, tooltip: str) -> None:
    """Will display a popup tooltip window that is scrollable and zoomable using
    mouse wheel + Ctrl

    Args:
        label (str): not utilized at the moment
        tooltip (str): tooltip text to be displayed
    """
    dialog = ToolTipWindow(label, tooltip)
    dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
    dialog.exec_()
