from PySide2.QtGui import QColor
import maya.cmds as mc #imports maya's cmd module so we can use it to do stuff in maya
from maya.OpenMaya import MVector
import maya.mel as mel

from PySide2.QtWidgets import QColorDialog, QLineEdit, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton # imports all the widgets needed to buil our ui
from PySide2.QtCore import Qt # this has some values we can use to configure our widget, like their windowType, or orientation
from MayaUtils import QMayaWindow

    
class LimbRigger:  # Class that handles the rigging of a limb with FK controls.
    def __init__(self): # Initializes the LimbRigger class.
        self.root = ""  # The root joint of the limb.
        self.mid = ""  # The middle joint of the limb.
        self.end = ""  # The end joint of the limb.
        self.controllerSize = 5  # The size of the FK controllers.
        #Pooo

    def AutoFindJnts(self): # Function to create FK controls for a given joint.
        self.root = mc.ls(sl=True, type="joint")[0]
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
        self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]

    def CreateFKControlForJnt(self, jntName): # Function to rig the entire limb by creating FK controls for each joint.
        ctrlName = "ac_fk_" + jntName
        ctrlGrpName = ctrlName + "_grp"
        mc.circle(n=ctrlName, r=self.controllerSize, nr = (1,0,0))

        mc.group(ctrlName, n=ctrlGrpName)
        mc.matchTransform(ctrlGrpName, jntName)
        mc.orientConstraint(ctrlName, jntName)
        return ctrlName, ctrlGrpName
    
    def CreateBoxController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 ;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name)
        mc.makeIdentity(name, apply = True)# this is freeze transformation

        grpName = name + "_grp"
        mc.group(name, n=grpName)
        return name, grpName
    
    def CreatePlusController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p -14 0 0 -p -14 1 0 -p -15 1 0 -p -15 2 0 -p -14 2 0 -p -14 3 0 -p -13 3 0 -p -13 2 0 -p -12 2 0 -p -12 1 0 -p -13 1 0 -p -13 0 0 -p -14 0 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 ;")
        mc.scale(self.controllerSize/3, self.controllerSize/3, self.controllerSize/3)
        mc.makeIdentity(name, apply = True)

        grpName = name + "_grp"
        mc.group(name, n=grpName)
        return name, grpName
    
    def GetObjectLoc(self, objectName)->MVector:
        x, y, z, = mc.xform(objectName, q=True, t=True, ws=True)# Get the world space translation of the objectName
        return MVector(x, y, z)
    
    def PrintMVector(self, vectorToPrint):
        print(f"<{vectorToPrint.x}, {vectorToPrint.y}, {vectorToPrint.z}>")

    def RigLimb(self, r, g, b): # Creates three  parented Fk controllers for all the joints
        rootFKCtrl, rootFKCtrlGrp = self.CreateFKControlForJnt(self.root)
        midFKCtrl, midFKCtrlGrp = self.CreateFKControlForJnt(self.mid)
        endFKCtrl, endFKCtrlGrp = self.CreateFKControlForJnt(self.end)

        mc.parent(midFKCtrlGrp, rootFKCtrl)
        mc.parent(endFKCtrlGrp, midFKCtrl)

        ikEndCtrl = "ac_ik_" + self.end
        ikEndCtrl, ikEndCtrlGrp = self.CreateBoxController(ikEndCtrl)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end)[0]

        rootJntLoc = self.GetObjectLoc(self.root)
        endJntLoc = self.GetObjectLoc(self.end)

        rootToEndVec = endJntLoc - rootJntLoc

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n=ikHandleName, sj=self.root, ee = self.end, sol="ikRPsolver")
        ikPoleVectorVals = mc.getAttr(ikHandleName + ".poleVector")[0]
        ikPoleVector = MVector(ikPoleVectorVals[0], ikPoleVectorVals[1], ikPoleVectorVals[2])

        ikPoleVector.normalize()
        ikPoleVectorCtrlLoc = rootJntLoc + rootToEndVec / 2 + ikPoleVector * rootToEndVec.length()

        ikPoleVectorCtrlName = "ac_ik_" + self.mid
        mc.spaceLocator(n=ikPoleVectorCtrlName)
        ikPoleVectorCtrlGrp = ikPoleVectorCtrlName + "_grp"
        mc.group(ikPoleVectorCtrlName, n=ikPoleVectorCtrlGrp)
        mc.setAttr(ikPoleVectorCtrlGrp+".t", ikPoleVectorCtrlLoc.x, ikPoleVectorCtrlLoc.y, ikPoleVectorCtrlLoc.z, typ = "double3")
        mc.poleVectorConstraint(ikPoleVectorCtrlName, ikHandleName)

        ikfkBlendCtrlName = "ac_ikfk_blend_" + self.root
        ikfkBlendCtrlName, ikfkBlendCtrlGrp = self.CreatePlusController(ikfkBlendCtrlName)
        ikfkBlendCtrlLoc = rootJntLoc + MVector(rootJntLoc.x, 0, rootJntLoc.z)
        mc.setAttr(ikfkBlendCtrlGrp+".t", ikfkBlendCtrlLoc.x, ikfkBlendCtrlLoc.y, ikfkBlendCtrlLoc.z, typ="double3")

        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikfkBlendCtrlName, ln=ikfkBlendAttrName, min=0, max=1, k=True)
        ikfkBlendAttr = ikfkBlendCtrlName + "." + ikfkBlendAttrName

        mc.expression(s=f"{ikHandleName}.ikBlend = {ikfkBlendAttr}")
        mc.expression(s=f"{ikEndCtrlGrp}.v = {ikPoleVectorCtrlGrp}.v = {ikfkBlendAttr}")
        mc.expression(s=f"{rootFKCtrlGrp}.v = 1 - {ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{endFKCtrl}W0 = 1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{ikEndCtrl}W1 = {ikfkBlendAttr}")

        mc.parent(ikHandleName, ikEndCtrl)
        mc.setAttr(ikHandleName+".v", 0)

        topGrpName = self.root + "_rig_grp"
        mc.group([rootFKCtrlGrp,ikEndCtrlGrp, ikPoleVectorCtrlGrp, ikfkBlendCtrlGrp], n= topGrpName)
        mc.setAttr(topGrpName+".overrideEnabled", 1)
        mc.setAttr(topGrpName+".overrideRGBColors", 1)
        mc.setAttr(topGrpName+".overrideColorRGB", r, g, b, type="double3")
        print("jobs Done!")
        print("jobs Done!")
        print("jobs Done!")

class ColorPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.colorPickerBtn = QPushButton()
        self.colorPickerBtn.setStyleSheet(f"background-color:black;")
        self.masterLayout.addWidget(self.colorPickerBtn)
        self.colorPickerBtn.clicked.connect(self.ColorPickerBtnClicked)
        self.color = QColor(0, 0, 0)

    def ColorPickerBtnClicked(self):
        self.color = QColorDialog.getColor()
        self.colorPickerBtn.setStyleSheet(f"background-color:{self.color.name()};")

class LimbRigToolWidget(QMayaWindow): # Creates the widgets that are in the LimbRigWindow
    def __init__(self): # Creates the button, texts, and slider widgets
        super().__init__()
        self.rigger = LimbRigger()
        self.setWindowTitle("Limb Rigging Tool")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.tipLabel = QLabel("Select the First Joint of the Limb, and click on the Auto Find Button")
        self.masterLayout.addWidget(self.tipLabel)

        self.jointSelectionText = QLineEdit()
        self.masterLayout.addWidget(self.jointSelectionText)
        self.jointSelectionText.setEnabled(False)

        self.autoFindBttn = QPushButton("Auto Find")
        self.masterLayout.addWidget(self.autoFindBttn)
        self.autoFindBttn.clicked.connect(self.AutoFindBttnClicked)

        ctrlSliderLayout = QHBoxLayout()
        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeValueChanged)
        ctrlSizeSlider.setRange(1, 30)
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSliderLayout.addWidget(ctrlSizeSlider)
        self.ctrlSizeLabel = QLabel(f"{self.rigger.controllerSize}")
        ctrlSliderLayout.addWidget(self.ctrlSizeLabel)

        self.masterLayout.addLayout(ctrlSliderLayout)

        self.colorPicker = ColorPicker()
        self.masterLayout.addWidget(self.colorPicker)

        self.rigLimbBttn = QPushButton("Rig Limb")
        self.masterLayout.addWidget(self.rigLimbBttn)
        self.rigLimbBttn.clicked.connect(self.RigLimbBttnClicked)

    def CtrlSizeValueChanged(self, newValue): # Changes controller size
        self.rigger.controllerSize = newValue
        self.ctrlSizeLabel.setText(f"{self.rigger.controllerSize}")

    def RigLimbBttnClicked(self): # Runs the RigLimb Function
        self.rigger.RigLimb(self.colorPicker.color.redF(), self.colorPicker.color.greenF(), self.colorPicker.color.blueF())

    def AutoFindBttnClicked(self): # Finds and set joints and gives error if selected incorrectly
        try: # Finds and sets joints 
            self.rigger.AutoFindJnts()
            self.jointSelectionText.setText(f"{self.rigger.root},{self.rigger.mid},{self.rigger.end}")
        except Exception as e: # Gives error message
            QMessageBox.critical(self, "Error", "Wrong Selection, Please select the first joint of a limb!")

limbRigToolWidget = LimbRigToolWidget() # Assigns a variable
limbRigToolWidget.show() # Shows window


