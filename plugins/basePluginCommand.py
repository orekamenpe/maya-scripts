import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys

commandName = "basePluginCommand"


class BasePluginCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)


    def doIt(self, argList):
        print "Do it..."


def creator():
    return OpenMayaMPx.asMPxPtr(BasePluginCommand())


def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, "orekamenpe", "1.0", "Any")
    try:
        plugin.registerCommand(commandName, creator)
    except:
        sys.stderr.write("Failed to register command :" + commandName)


def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterCommand(commandName)
    except:
        sys.stderr.write("Failed to de-register command:" + commandName)
