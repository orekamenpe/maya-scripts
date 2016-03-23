import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaFX as OpenMayaFX
import sys


commandName = "vertexParticle"

kHelpFlag = "-h"
kHelpLongFlag = "-help"
kSparseFlag = "-s"
kSparseLongFlag = "-sparse"
helpMessage = "This command is used to attach a particle on each vertex of a poly mesh"


class PluginCommand(OpenMayaMPx.MPxCommand):

    mObj_particle = OpenMaya.MObject()
    sparse = None

    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)


    def argumentParser(self, argList):
        syntax = self.syntax()

        try:
            parsedArguments = OpenMaya.MArgDatabase(syntax, argList)
        except:
            print "Incorrect Argument"
            return "unknown"

        if parsedArguments.isFlagSet(kSparseFlag):
            self.sparse = parsedArguments.flagArgumentDouble(kSparseFlag, 0)
            return None
        if parsedArguments.isFlagSet(kSparseLongFlag):
            self.sparse = parsedArguments.flagArgumentDouble(kSparseLongFlag, 0)
            return None
        if parsedArguments.isFlagSet(kHelpFlag):
            self.setResult(helpMessage)
            return None
        if parsedArguments.isFlagSet(kHelpLongFlag):
            self.setResult(helpMessage)
            return None


    def isUndoable(self):
        return True


    def undoIt(self):
        mFnDagNode = OpenMaya.MFnDagNode(self.mObj_particle)
        mDagMod = OpenMaya.MDagModifier()
        if self.mObj_particle.apiTypeStr() != "kInvalid":
            mDagMod.deleteNode(mFnDagNode.parent(0))
            mDagMod.doIt()
            self.mObj_particle = OpenMaya.MObject()
        return None


    def redoIt(self):
        mSel = OpenMaya.MSelectionList()
        mDagPath = OpenMaya.MDagPath()
        mFnMesh = OpenMaya.MFnMesh()

        OpenMaya.MGlobal.getActiveSelectionList(mSel)
        if mSel.length() >= 1:
            try:
                mSel.getDagPath(0,mDagPath)
                mFnMesh.setObject(mDagPath)
            except:
                print "Select a poly mesh, please"
                return "unknown"
        else:
            print "Select a poly mesh, please"
            return "unknown"

        mPointArray = OpenMaya.MPointArray()
        mFnMesh.getPoints(mPointArray, OpenMaya.MSpace.kWorld)

        #Create a particle system
        mFnParticle = OpenMayaFX.MFnParticleSystem()
        self.mObj_particle = mFnParticle.create()
        print "Created"

        #To fix Maya bug
        mFnParticle = OpenMayaFX.MFnParticleSystem(self.mObj_particle)
        counter = 0
        for i in xrange(mPointArray.length()):
            if i%self.sparse==0:
                mFnParticle.emit(mPointArray[i])
                counter += 1
        print "Total Points: " + str(counter)
        mFnParticle.saveInitialState()
        return None


    def doIt(self, argList):
        print "creating Particles"
        self.argumentParser(argList)
        print self.sparse
        if self.sparse != None:
            self.redoIt()
        return None


# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr(PluginCommand())


def syntaxCreator():
    # create MSyntax object
    syntax = OpenMaya.MSyntax()

    # collect/add the flags
    syntax.addFlag(kHelpFlag, kHelpLongFlag)
    syntax.addFlag(kSparseFlag, kSparseLongFlag, OpenMaya.MSyntax.kDouble)

    # return MSyntax
    return syntax


# Initialize the script plug-in
def initializePlugin(mObj):
    plugin = OpenMayaMPx.MFnPlugin(mObj, "orekamenpe", "1.0", "Any")
    try:
        plugin.registerCommand(commandName, cmdCreator, syntaxCreator)
    except:
        sys.stderr.write("Failed to register command: %s\n" % commandName)


# Uninitialize the script plug-in
def uninitializePlugin(mObj):
    plugin = OpenMayaMPx.MFnPlugin(mObj)
    try:
        plugin.deregisterCommand(commandName)
    except:
        sys.stderr.write("Failed to de-register command: " + commandName)