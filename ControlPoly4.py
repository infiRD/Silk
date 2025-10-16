#    This file is part of Silk
#    (c) Edward Mills 2016-2017
#    edwardvmills@gmail.com
#
#    NURBS Surface modeling tools focused on low degree and seam continuity (FreeCAD Workbench)
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

# spellchecker: ignore Arach NURBS pixmap

from __future__ import division  # allows floating point division from integers

import FreeCAD as App
import FreeCADGui as Gui

import ArachNURBS as AN
import Silk_tooltips
from popup import tipsDialog

# get strings
tooltip = Silk_tooltips.ControlPoly4_baseTip + Silk_tooltips.standardTipFooter
moreInfo = Silk_tooltips.ControlPoly4_baseTip + Silk_tooltips.ControlPoly4_moreInfo

# Locate Workbench Directory & icon
import os

import Silk_dummy

path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons = os.path.join(path_Silk, "Resources", "Icons")
iconPath = path_Silk_icons + "/ControlPoly4.svg"


class ControlPoly4:
    def Activated(self):
        sel = Gui.Selection.getSelectionEx()
        mode = None
        SelectedEdge = None

        if len(sel) == 0:
            # empty selection - show tool information window
            tipsDialog("Silk: ControlPoly4", moreInfo)
            return

        elif len(sel) == 1:
            # one object selected for input
            if sel[0].Object.TypeId in [
                "Sketcher::SketchObject",
                "PartDesign::ShapeBinder",
                "PartDesign::SubShapeBinder",
                "Part::Part2DObjectPython",
                "Part::Compound",
            ]:
                if len(sel[0].Object.Shape.Edges) == 3:
                    # which contains exactly 3 edges
                    mode = "3L"
                else:
                    # any other number of edges will only consider the first element (in the geometry listing)
                    mode = "FirstElement"
            else:
                # is it a ControlGrid44_4?
                try:
                    if sel[0].Object.object_type == "ControlGrid44_4":
                        mode = "GridEdge"

                        poles = sel[0].Object.Poles
                        edge0p = [1, 2]
                        edge1p = [7, 11]
                        edge2p = [13, 14]
                        edge3p = [4, 8]

                        if sel[0].SubObjects[0].ShapeType == "Vertex":
                            v0 = sel[0].SubObjects[0].Point
                            # p0 = poles.index(v0) - worked in console, but not here. decimal places are mismatched?
                            p0 = AN.VectorIndex(poles, v0)
                            if p0 in edge0p:
                                SelectedEdge = 0
                            elif p0 in edge1p:
                                SelectedEdge = 1
                            elif p0 in edge2p:
                                SelectedEdge = 2
                            elif p0 in edge3p:
                                SelectedEdge = 3
                            else:
                                print("ControlPoly4: 'GridEdge' mode. The selected grid vertex is not on an edge, the input cannot be interpreted")
                                return

                        elif sel[0].SubObjects[0].ShapeType == "Edge":
                            v0 = sel[0].SubObjects[0].firstVertex().Point
                            v1 = sel[0].SubObjects[0].lastVertex().Point
                            # p0 = poles.index(v0) - worked in console, but not here. decimal places are mismatched?
                            # p1 = poles.index(v1) - worked in console, but not here. decimal places are mismatched?
                            p0 = AN.VectorIndex(poles, v0)
                            p1 = AN.VectorIndex(poles, v1)
                            if p0 in edge0p:
                                SelectedEdge = 0
                            elif p0 in edge1p:
                                SelectedEdge = 1
                            elif p0 in edge2p:
                                SelectedEdge = 2
                            elif p0 in edge3p:
                                SelectedEdge = 3
                            if p1 in edge0p:
                                SelectedEdge = 0
                            elif p1 in edge1p:
                                SelectedEdge = 1
                            elif p1 in edge2p:
                                SelectedEdge = 2
                            elif p1 in edge3p:
                                SelectedEdge = 3
                            else:
                                print("ControlPoly4: 'GridEdge' mode. The selected grid line is not along an edge, the input cannot be interpreted")
                                return

                        else:
                            print("GridEdge mode failed to identify either a vertex or an edge in the selection")
                            return
                        # print("SelectedEdge index = ", SelectedEdge)

                except Exception:
                    pass

        elif len(sel) == 2:
            if sel[0].Object.TypeId == "Sketcher::SketchObject" and sel[1].Object.TypeId == "Sketcher::SketchObject":
                mode = "2N"
            else:
                try:
                    if sel[0].Object.object_type == "Point_onCurve" and sel[1].Object.object_type == "Point_onCurve":
                        mode = "2P"
                except Exception:
                    pass

        print("ControlPoly4 input selection interpreted as ", mode)

        cp4 = None
        if mode == "3L":
            sketch = Gui.Selection.getSelection()[0]
            cp4 = App.ActiveDocument.addObject("Part::FeaturePython", "ControlPoly4_3L_000")
            AN.ControlPoly4_3L(cp4, sketch)

        elif mode == "FirstElement":
            sketch = Gui.Selection.getSelection()[0]
            cp4 = App.ActiveDocument.addObject("Part::FeaturePython", "ControlPoly4_FirstElement_000")
            AN.ControlPoly4_FirstElement(cp4, sketch)

        elif mode == "GridEdge":
            grid = Gui.Selection.getSelection()[0]
            if not SelectedEdge:
                raise RuntimeError("SelectedEdge was not set in previous code block")
            edge = SelectedEdge
            cp4 = App.ActiveDocument.addObject("Part::FeaturePython", "ControlPoly4_GridEdge_000")
            raise NotImplementedError("ControlPoly4_GridEdge not implemented yet")
            AN.ControlPoly4_GridEdge(cp4, grid, edge)

        elif mode == "2N":
            sketch0 = Gui.Selection.getSelection()[0]
            sketch1 = Gui.Selection.getSelection()[1]
            cp4 = App.ActiveDocument.addObject("Part::FeaturePython", "ControlPoly4_2N_000")
            AN.ControlPoly4_2N(cp4, sketch0, sketch1)

        elif mode == "2P":
            Point0 = Gui.Selection.getSelection()[0]
            Point1 = Gui.Selection.getSelection()[1]
            cp4 = App.ActiveDocument.addObject("Part::FeaturePython", "ControlPoly4_2P_000")
            AN.ControlPoly4_2P(cp4, Point0, Point1)

        else:
            print("Selection not recognized, check tooltip")

        if cp4:
            cp4.ViewObject.Proxy = 0  # just set it to something different from None (this assignment is needed to run an internal notification)
            cp4.ViewObject.LineWidth = 1.00
            cp4.ViewObject.LineColor = (0.00, 1.00, 1.00)
            cp4.ViewObject.PointSize = 4.00
            cp4.ViewObject.PointColor = (0.00, 0.00, 1.00)
            App.ActiveDocument.recompute()

    def GetResources(self):
        return {"Pixmap": iconPath, "MenuText": "ControlPoly4", "ToolTip": tooltip}


Gui.addCommand("ControlPoly4", ControlPoly4())
