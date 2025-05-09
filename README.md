# Maya Plugins

This is a collection of maya plugins to help with rigging and other stuff

# How to install:
drag the install.el file into maya's viewport, and the tools will appear on the current shelf.

## Limb Rigger

Rigs any 3 joint limb.

* Auto find the joints
* Control the controller size
* Control the Controller color
* Modular approach

## Space Switcher

You select a control (driven object).


You then add multiple "space" parent objects.


The script creates an enum switch (spaceSwitch) on the control.


Based on the enum value, a condition node activates the appropriate constraint target, allowing space switching.