from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox, QComboBox
from PySide2.QtCore import Qt
import maya.cmds as mc

class SpaceSwitchTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Space Switch Tool")
        self.setMinimumWidth(300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.targetLabel = QLabel("Select Control (Driven):")
        self.layout.addWidget(self.targetLabel)

        self.controlField = QLineEdit()
        self.controlField.setPlaceholderText("Driven object (e.g., CTRL)")
        self.layout.addWidget(self.controlField)

        self.getControlBtn = QPushButton("Load Selected Control")
        self.getControlBtn.clicked.connect(self.LoadSelectedControl)
        self.layout.addWidget(self.getControlBtn)

        self.spaceLabel = QLabel("Add Parent Spaces:")
        self.layout.addWidget(self.spaceLabel)

        self.parentList = QComboBox()
        self.layout.addWidget(self.parentList)

        self.addParentBtn = QPushButton("Add Selected as Parent Space")
        self.addParentBtn.clicked.connect(self.AddSelectedParent)
        self.layout.addWidget(self.addParentBtn)

        self.createSwitchBtn = QPushButton("Create Space Switch")
        self.createSwitchBtn.clicked.connect(self.CreateSpaceSwitch)
        self.layout.addWidget(self.createSwitchBtn)

        self.control = ""
        self.parents = []

    def LoadSelectedControl(self):
        sel = mc.ls(sl=True)
        if sel:
            self.control = sel[0]
            self.controlField.setText(self.control)
        else:
            QMessageBox.warning(self, "Warning", "Please select a control.")

    def AddSelectedParent(self):
        sel = mc.ls(sl=True)
        if sel:
            parent = sel[0]
            if parent not in self.parents:
                self.parents.append(parent)
                self.parentList.addItem(parent)
        else:
            QMessageBox.warning(self, "Warning", "Please select a parent space.")

    def CreateSpaceSwitch(self):
        if not self.control or not self.parents:
            QMessageBox.critical(self, "Error", "Please specify both control and parent spaces.")
            return

        switchAttr = "spaceSwitch"
        if not mc.objExists(f"{self.control}.{switchAttr}"):
            mc.addAttr(self.control, ln=switchAttr, at="enum", en=":".join(self.parents), k=True)

        constGroup = mc.group(em=True, name=self.control + "_const_grp")
        mc.delete(mc.parentConstraint(self.control, constGroup))
        mc.parent(constGroup, self.control)
        mc.makeIdentity(constGroup, apply=True, t=1, r=1, s=1)

        constraints = []
        for parent in self.parents:
            const = mc.parentConstraint(parent, constGroup, mo=True)[0]
            constraints.append(const)

        for i, parent in enumerate(self.parents):
            cond = mc.shadingNode("condition", asUtility=True, name=f"{self.control}_spaceCond_{i}")
            mc.setAttr(f"{cond}.secondTerm", i)
            mc.setAttr(f"{cond}.operation", 0)  # Equals
            mc.connectAttr(f"{self.control}.{switchAttr}", f"{cond}.firstTerm")
            mc.setAttr(f"{cond}.colorIfTrueR", 1)
            mc.setAttr(f"{cond}.colorIfFalseR", 0)
            mc.connectAttr(f"{cond}.outColorR", f"{constraints[0]}.{parent}W{i}")

        QMessageBox.information(self, "Success", "Space switch setup complete!")

# Run the tool in Maya
def RunSpaceSwitchTool():
    global spaceSwitchTool
    try:
        spaceSwitchTool.close()
    except:
        pass
    spaceSwitchTool = SpaceSwitchTool()
    spaceSwitchTool.show()
