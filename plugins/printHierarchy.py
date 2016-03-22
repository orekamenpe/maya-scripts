import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys


commandName = "printHierarchy"


class pluginCommand(OpenMayaMPx.MPxCommand):

    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt(self, argList):
        print "Scene Hierarchy" # delete prints in production
        dagIterator = OpenMaya.MItDag(OpenMaya.MItDag.kDepthFirst, OpenMaya.MFn.kInvalid)
        dagNodeFn = OpenMaya.MFnDagNode()

        while (not dagIterator.isDone()):
            currentObj = dagIterator.currentItem()
            depth = dagIterator.depth()
            dagNodeFn.setObject(currentObj)

            name = dagNodeFn.name()
            type = currentObj.apiTypeStr()
            path = dagNodeFn.fullPathName()

            printOut = ""
            for i in range(0, depth):
                printOut += "----->"

            printOut += "name: " + name + ", Type: " + type + ", Path: " + path
            print printOut

            dagIterator.next()


def cmdCreator():
    return OpenMayaMPx.asMPxPtr(pluginCommand())


def initializePlugin(mObj):
    plugin = OpenMayaMPx.MFnPlugin(mObj)
    try:
        plugin.registerCommand(commandName,cmdCreator)
    except:
        sys.stderr.write("Failed to register command: " + commandName)


def uninitializePlugin(mObj):
    plugin = OpenMayaMPx.MFnPlugin(mObj)
    try:
        plugin.deregisterCommand(commandName)
    except:
        sys.stderr.write("Failed to de-register command: " + commandName)