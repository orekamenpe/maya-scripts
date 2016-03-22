import maya.cmds as cmds
import maya.mel as mel
import string

""" move to maya scripts folder
    Libraries > Documents > My Documents > maya > scripts 
	or OneDrive > Documents > maya > scripts

	load the script:
	import FBXAnimationExporter
    reload(FBXAnimationExporter)
    FBXAnimationExporter.FBXExporter_UI()
	"""
mel.eval("source FBXAnimationExporter_FBXOptions.mel")

def tagForOrigin(node):
    """ Tag the given node with the origin attribute and set true

    Procedure: If the object exists, and the attribute does not exist,
    add the origin bool attribute and set to true
    """
    if cmds.objExists(node):
        if not cmds.objExists(node + ".origin"):
            cmds.addAttr(node, shortName="org", longName="origin", at="bool")
        # endif
        cmds.setAttr(node + ".origin", True)
    # endif


def tagForMeshExport(mesh):
    """ Add attributes to the mesh so exporter can find them

        Procedure: If object exists, and the attribute does not, add exportMeshes message attribute
    """
    if cmds.objExists(mesh):
        if not cmds.objExists(mesh + ".exportMeshes"):
            cmds.addAttr(mesh, shortName="xms", longName="exportMeshes", at="message")


def tagForExportNode(node):
    """ Add attribute to the node so export can find export definitions

        Procedure: If the object exists, and the attribute does not exist,
            add the exportNode message attribute
    """
    if cmds.objExists(node):
        if not cmds.objExists(node + ".exportNode"):
            cmds.addAttr(node, shortName="xnd", longName="exporNode", at="message")

def returnOrigin(ns):
    """ Return the origin of the given namespace

        Procedure: If ns (namespace) is not empty string, list all joints with the matching namespace, else list all joints
            for list of joints, look for origin attribute and if it is set to true. If found, return name of joint,
             else return "Error"

        Presumption: Origin attribute is on a joint
            "Error" is not a valid joint name
            namespace does not include colon
    """
    joints=[]

    if ns:
        joints = cmds.ls((ns + ":*"), type="joint")
    else:
        joints = cmds.ls(type="joint")

    if len(joints):
        for curJoint in joints:
            if cmds.objExists(curJoint + ".origin") and cmds.getAttr(curJoint + ".origin"):
                return curJoint
    return "Error"


def clearGarbage():
    """ Removes all nodes taged as garbage

        Procedure: List all transforms in the scene
            Iterate through list, anything with "deleteMe" attribute will be deleted

        Presumption: The deleteMe attribute is name of the attribute signifying garbage
    """
    list = cmds.ls(tr=True) #get all transforms

    for cur in list:
        if cmds.objExists(cur + ".deleteMe"):
            cmds.delete(cur)


def tagForGarbage(node):
    """ Tag object for being garbage

        Procedure: If node is valid object and attribute does not exists, add deleteMe attribute
    """
    if cmds.objExists(node):
       if not cmds.objExists(node + ".deleteMe"):
           cmds.addAttr(node, shortName="del", longName="deleteMe", at="bool")
       #endif
       cmds.setAttr(node + ".deleteMe", True)
    #endif



def findMeshesWithBlendshapes(ns):
    """ Return the meshes connected to blendshape nodes

        Procedure: Get a list of blendshape nodes
            Follow those connections to the mesh shape node
            Traverse up the hierarchy to find parent transform node

        Presumptions: Character has a valid namespace, namespace does not have colon
            only exporting polygonal meshes
    """
    returnArray = []

    blendshapes = cmds.ls((ns + ":*"), type="blendShape")

    for curBlendShape in blendshapes:
        downstreamNodes = cmds.listHistory(curBlendShape, future=True)
        for curNode in downstreamNodes:
            if cmds.objectType(curNode, type="mesh"):
                parents = cmds.listRelatives(curNode, parent=True)
                returnArray.append(parents[0])

    return returnArray


#######################################
#
#    Export settings node procs
#
#######################################
def returnFBXExportNodes(origin):
    """ Return all export nodes connected to given origin

        Procedure: if origin is valid and has the exportNode attribute,
            return list of export nodes connected to it

        Presumption: Only export nodes are connected to exportNode attribute
    """
    exportNodeList = []

    if cmds.objExists(origin + ".exportNode"):
        exportNodeList = cmds.listConnections(origin + ".exportNode")

    return exportNodeList


def connectFBXExportNodeToOrigin(exportNode, origin):
    """ Connect the fbx export node to the origin

        Procedure: check if attribute exists and nodes are valid
            if they are, connect attributes
    """

    if cmds.objExists(origin) and cmds.objExists(exportNode):
        if not cmds.objExists(origin + ".exportNode"):
            tagForExportNode(origin)

        if not cmds.objExists(exportNode + ".exportNode"):
            addFBXNodeAttrs(exportNode)

        cmds.connectAttr(origin + ".exportNode", exportNode + ".exportNode")


def deleteFBXExportNode(exportNode):
    """ Delete given export node

        Procedure: if object exists, delete
    """
    if cmds.objExists(exportNode):
        cmds.delete(exportNode)



def addFBXNodeAttrs(fbxExportNode):
    """ To add the attribute to the export node to store our export settings

        Procedure: for each attribute we want to add, check if it exists
            If it doesnt exist, add

        Presumptions: Assume fbxExportNode is valid object
    """
    if not cmds.attributeQuery("export", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="export", at="bool")

    if not cmds.attributeQuery("moveToOrigin", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName='moveToOrigin', at="bool")

    if not cmds.attributeQuery("zeroOrigin", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName='zeroOrigin', at="bool")

    if not cmds.attributeQuery("exportName", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName='exportName', dt="string")

    if not cmds.attributeQuery("useSubRange", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName='useSubRange', at="bool")

    if not cmds.attributeQuery("startFrame", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName='startFrame', at="float")

    if not cmds.attributeQuery("endFrame", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName='endFrame', at="float")

    if not cmds.attributeQuery("exportMeshes", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName='exportMeshes', at="message")

    if not cmds.attributeQuery("exportNode", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, shortName="xnd", longName='exportNode', at="message")

    if not cmds.attributeQuery("animLayers", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName='animLayers', dt="string")


def createFBXExportNode(characterName):
    """ create the export node to store our export settings

        Procedure: create an empty transform node
            we will send it o addFBXNodeAttrs to add the needed attributes
    """
    fbxExportNode = cmds.group(em=True, name=characterName + "FBXExportNode#")
    addFBXNodeAttrs(fbxExportNode)
    cmds.setAttr(fbxExportNode + ".export", 1)
    return fbxExportNode


#############################
#
#    Model export procs
#
#############################

def connectFBXExportNodeToMeshes(exportNode, meshes):
    """ To connect meshes to export node so the exporter can find them

        Procedure: check to make sure meshes and exportNode is valid,
            check for atribute "exportMeshes". If no atribute, add it. Then connect attributes

        Presumptions: exportNode is a exportNode, and meshes is a list of transform nodes for polygon meshes
    """
    if cmds.objExists(exportNode):

        if not cmds.objExists(exportNode + ".exportMeshes"):
            addFBXNodeAttrs(exportNode)

        for curMesh in meshes:
            if cmds.objExists(curMesh):
                if not cmds.objExists(curMesh + ".exportMeshes"):
                    tagForMeshExport(curMesh)

                cmds.connectAttr(exportNode + ".exportMeshes", curMesh + ".exportMeshes", force=True)


def disconnectFBXExportNodeToMeshes(exportNode, meshes):
    """ Disconnect the message attribute between export node and mesh

        Procedure: Iterate through list of meshes and if mesh exists, disconnect

        Presumption: that node and mesh are conneced via exportMeshes message attr
    """
    if cmds.objExists(exportNode):
        for curMesh in meshes:
            if cmds.objExists(curMesh):
                cmds.disConnectAttr(exportNode + ".exportMeshes", curMesh + ".exportMeshes")


def returnConnectedMeshes(exportNode):
    """ Return a list of all meshes conneced to the export node

    Procedure: listConnections to exportMeshes attribute

    Presumption: exportMeshes attribute is used to connect to export meshes,
        exportMeshes is valid
    """
    meshes = cmds.listConnections((exportNode + ".exportMeshes"), source=False, destination=True)
    return meshes


#############################
#
#    Animation export procs
#
#############################


def unlockJointTransforms(root):
    """
    """
    hierarchy=cmds.listRelatives(root, ad=True, f=True)

    hierarchy.append(root)

    for cur in hierarchy:
		cmds.setAttr( (cur + '.translateX'), lock=False )
		cmds.setAttr( (cur + '.translateY'), lock=False )
		cmds.setAttr( (cur + '.translateZ'), lock=False )
		cmds.setAttr( (cur + '.rotateX'), lock=False )
		cmds.setAttr( (cur + '.rotateY'), lock=False )
		cmds.setAttr( (cur + '.rotateZ'), lock=False )
		cmds.setAttr( (cur + '.scaleX'), lock=False )
		cmds.setAttr( (cur + '.scaleY'), lock=False )
		cmds.setAttr( (cur + '.scaleZ'), lock=False )


def connectAttrs(sourceNode, destNode, transform):
    """ to connect given node to other given node via specified transform

        Procedure: call connectAttr

        Presumptions: assume two nodes exist and transform type is valid
    """
    cmds.connectAttr(sourceNode + "." + transform + "X", destNode + "." + transform + "X")
    cmds.connectAttr(sourceNode + "." + transform + "Y", destNode + "." + transform + "Y")
    cmds.connectAttr(sourceNode + "." + transform + "Z", destNode + "." + transform + "Z")

def copyAndConnectSkeleton(origin):
    """ To Copy the bind skeleton and connect the copy to the original bind

        Procedure: duplicate hierarchy
            delete everything that is not a joint
            unlock all the joints
            connect the translates, rotates, and scales
            parent copy to the world
            add deleteMe attr

        Presumptions: No joints are children of anything but other joints
    """
    newHierarchy = []

    if origin != "Error" and cmds.objExists(origin):
        dupHierarchy = cmds.duplicate(origin)
        tempHierarchy = cmds.listRelatives(dupHierarchy[0], allDescendents=True, fullPath=True)

        for cur in tempHierarchy:
            if cmds.objExists(cur):
                if cmds.objectType(cur) != "joint":
                    cmds.delete(cur)

        unlockJointTransforms(dupHierarchy[0])

        origHierarchy = cmds.listRelatives(origin, ad=True, type="joint")
        newHierarchy = cmds.listRelatives(dupHierarchy[0], ad=True, type="joint")

        origHierarchy.append(origin)
        newHierarchy.append(dupHierarchy[0])

        for index in range(len(origHierarchy)):
        	connectAttrs(origHierarchy[index], newHierarchy[index], "translate")
        	connectAttrs(origHierarchy[index], newHierarchy[index], "rotate")
        	connectAttrs(origHierarchy[index], newHierarchy[index], "scale")

        cmds.parent(dupHierarchy[0], world=True)
        tagForGarbage(dupHierarchy[0])

    return newHierarchy


def transformToOrigin(origin, startFrame, endFrame, zeroOrigin):
    """ Translate export skeleton to origin. May or may not kill origin animation depending on input

        Procedure: bake the animation into our origin
            create an animLayer
            animLayer will either be additive or overrride depending on parameter we pass
            add deleteMe attr to animLayer
            move to origin

        Presumption: origin is valid, end frame is greater than start frame, zeroOrigin is boolean
    """
    cmds.bakeResults(origin, t=(startFrame, endFrame), at= ["rx","ry","rz","tx","ty","tz","sx","sy","sz"], hi="none")

    cmds.select(clear=True)
    cmds.select(origin)

    newNaimLayer = ""

    if zeroOrigin:
        #kills origin animation
        newAnimLayer = cmds.animLayer(aso=True, mute=False, solo=False, override=True, passthrough=True, lock=False)
        cmds.setAttr(newAnimLayer + ".rotationAccumulationMode", 0)
        cmds.setAttr(newAnimLayer + ".scaleAccumulationMode", 1)
    else:
        #shifts origin animation
        newAnimLayer = cmds.animLayer(aso=True, mute=False, solo=False, override=False, passthrough=False, lock=False)

    tagForGarbage(newAnimLayer)

    #turn anim layer on
    cmds.animLayer(newAnimLayer, edit=True, weight=1)
    cmds.setKeyframe(newAnimLayer + ".weight")

    #move origin animation to world origin
    cmds.setAttr(origin + ".translate", 0,0,0)
    cmds.setAttr(origin + ".rotate", 0,0,0)
    cmds.setKeyframe(origin, al=newAnimLayer, t=startFrame)

#############################
#
#    AnimLayers procs
#
#############################

def setAnimLayerSettings(exportNode):
    """ Record the animLayer settings used in animation and store in
        the exportNode as a string

        Procedure: List all the animLayers. Query their mute and solo attributes.
            List them in one single string
            Uses ; as sentinal value to split seperate animLayers
            Uses , as sentinal value to split seperate fields for animLayer
            Uses=as sentinal value to split seperate attrs from thier values in field
    """

    if not cmds.attributeQuery("animLayers", node=exportNode, exists=True):
        addFBXNodeAttrs(exportNode)

    animLayers = cmds.ls(type="animLayer")

    animLayerCommandStr=""

    for curLayer in animLayers:
        mute = cmds.animLayer(curLayer, query=True, mute=True)
        solo = cmds.animLayer(curLayer, query=True, solo=True)
        animLayerCommandStr += (curLayer + ", mute=" + str(mute) + ", solo=" + str(solo) + ";")

    cmds.setAttr(exportNode + ".animLayers", animLayerCommandStr, type="string")


def setAnimLayersFromSettings(exportNode):
    """ Set the animLayers based on the string value in the exportNode

        Procedure: Use pre-defined sentinal values to split the string for seperate animLayers
            And parse out the attributes and their values, then set

        Presumptions: Uses ; as sentinal value to split seperate animLayers
            Uses , as sentinal value to split seperate fields for animLayer
            Uses=as sentinal value to split seperate attrs from thier values in field
            order is Layer, mute, solo
    """

    if cmds.objExists(exportNode)and cmds.objExists(exportNode + ".animLayers"):
        animLayersRootString = cmds.getAttr(exportNode + ".animLayers", asString=True)

        if animLayersRootString:
            animLayerEntries = animLayersRootString.split(";")

            for curEntry in animLayerEntries:
                if curEntry:
                    fields = curEntry.split(",")

                    animLayerField = fields[0]
                    curMuteField = fields[1]
                    curSoloField = fields[2]

                    muteFieldStr = curMuteField.split("=")
                    soloFieldStr = curMuteField.split("=")

                    #convert strings to bool values
                    muteFieldBool = True
                    soloFieldBool = True

                    if muteFieldStr[1] != "True":
                        muteFieldBool = False

                    if soloFieldStr[1] != "True":
                        soloFieldBool = False

                    cmds.animLayer(animLayerField, edit=True, mute=muteFieldBool, solo=soloFieldBool)


def clearAnimLayerSettings(exportNode):
    """ Clear the anim layers from the exportNode """
    cmds.setAttr(exportNode + ".animLayers", "", type="string")


#############################
#
#    Export procs
#
#############################

def exportFBX(exportNode):
    curWorkspace = cmds.workspace(q=True, rd=True)
    fileName = cmds.getAttr(exportNode + ".exportName")

    if fileName:
        newFBX = curWorkspace + fileName
        cmds.file(newFBX, force=True, type='FBX export', pr=True, es=True)
    else:
        cmds.warning("No Valid Export Filename for Export Node " + exportNode + "\n")



def exportFBXAnimation(characterName, exportNode):

    clearGarbage()
    characters = []

    if characterName:
        characters.append(characterName)
    else:
        references = cmds.file(reference=1, query=True)
        for curRef in references:
            characters.append(cmds.file(curRef, namespace=1, query=True))

    for curCharacter in characters:

        #get meshes with blendshapes
        meshes = findMeshesWithBlendshapes(curCharacter)

        #get origin
        origin = returnOrigin(curCharacter)

        exportNodes = []

        if exportNode:
            exportNodes.append(exportNode)
        else:
            exportNodes = returnFBXExportNodes(origin)


        for curExportNode in exportNodes:
            if cmds.getAttr(curExportNode + ".export") and origin != "Error":
                exportRig = copyAndConnectSkeleton(origin)

                startFrame = cmds.playbackOptions(query=True, minTime=1)
                endFrame = cmds.playbackOptions(query=True, maxTime=1)

                subAnimCheck = cmds.getAttr(curExportNode + ".useSubRange")

                if subAnimCheck:
                    startFrame = cmds.getAttr(curExportNode + ".startFrame")
                    endFrame = cmds.getAttr(curExportNode + ".endFrame")

                if cmds.getAttr(curExportNode + ".moveToOrigin"):
                    newOrigin = cmds.listConnections(origin + ".translateX", source=False, d=True)
                    zeroOriginFlag = cmds.getAttr(curExportNode + ".zerOrigin")
                    transformToOrigin(newOrigin[0], startFrame, endFrame, zeroOriginFlag)

                cmds.select(clear=True)
                cmds.select(exportRig, add=True)
                cmds.select(meshes, add=True)

                setAnimLayersFromSettings(curExportNode)

                mel.eval("SetFBXExportOptions_animation(" + str(startFrame) + "," + str(endFrame) + ")")

                exportFBX(curExportNode)

            clearGarbage()


def exportFBXCharacter(exportNode):
    origin = returnOrigin("")

    exportNodes=[]

    if exportNode:
        exportNodes.append(exportNode)
    else:
        exportNodes = returnFBXExportNodes(origin)

    parentNode = cmds.listRelatives(origin, parent=True, fullPath=True)

    if parentNode:
        cmds.parent(origin, world=True)

    for curExportNode in exportNodes:
        if cmds.getAttr(curExportNode + ".export"):
            mel.eval("SetFBXExportOptions_model()")

            cmds.select(clear=True)

            meshes=returnConnectedMeshes(exportNode)

            cmds.select(origin, add=True)
            cmds.select(meshes, add=True)

            exportFBX(curExportNode)

        if parentNode:
            cmds.parent(origin, parentNode[0])



####################################################################################
#
#      U I       C O D E
#
####################################################################################


#########################################
#
#     Model UI Procs
#
#########################################

def FBXExporterUI_PopulateModelRootJointsPanel(ui_winModOriTextScrollList):
    """ Populate the root joints panel in the model tab

        Procedure: it will search for the origin. if none found, list all joints in the scene

        Presumption: origin is going to be a joint, rigs are not referenced in
    """

    cmds.textScrollList(ui_winModOriTextScrollList, edit=True, removeAll=True)

    origin = returnOrigin("")

    if origin != "Error":
        cmds.textScrollList(ui_winModOriTextScrollList, edit=True, ebg=False, append=origin)
    else:
        joints = cmds.ls(type="joint")
        for curJoint in joints:
            cmds.textScrollList(ui_winModOriTextScrollList, edit=True, bgc=[1, 0.1, 0.1], append=curJoint)

def FBXExporterUI_PopulateAniamtionActorPanel():
    pass

######################################
#
# Animation UI Procs
#
######################################

def FBXExporterUI_PopulateAnimationActorPanel(ui_windowAnimActorsTextScrollList):
    """ To populate the actor panel in the UI
        
        Procedure: get list of all references in the scene
            for each reference, get the namespace
            call returnOrigin for each namespace.
            if not "Error", add namespace to textScrollList
            
        Presumption: single-layered referencing, references have namespace
    """
    
    cmds.textScrollList(ui_windowAnimActorsTextScrollList, edit=True, removeAll=True)
    
    references = cmds.file(query=True, reference=True)
    
    for curRef in references:
        if not cmds.file(curRef, query=True, deferReference=True):
            ns = cmds.file(curRef, query=True, namespace=True)
            origin = returnOrigin(ns)
            
            if origin != "Error":
                cmds.textScrollList(ui_windowAnimActorsTextScrollList, edit=True, append=ns)              

def FBXExporterUI_UpdateExportNodeFromModelSettings():
    pass

def FBXExporterUI_PopulateModelsExportNodesPanel():
    pass

def FBXExporterUI_PopulateGeomPanel():
    pass

def FBXExporterUI_ModelExportAllCharacters():
    pass

def FBXExporterUI_ModelTagForOrigin():
    pass

def FBXExporterUI_ModelCreateNewExportNode():
    pass

def FBXExporterUI_ModelAddRemoveMeshes():
    pass

def FBXExporterUI_BrowseExportFilename(value):
    pass

def FBXExporterUI_ModelExportAllCharacters():
    pass

def FBXExporterUI_ModelExportSelectedCharacter():
    pass

def FBXExporterUI_ModelExportAllCharacters():
    pass

##########################
#
# Help windows
#
#########################

def FBXExporter_AnimationHelpWindow():
    ui_animHelpWindow = "ui_FBXExporter_AnimationHelpWindow"
    if cmds.window(ui_animHelpWindow, exists=True):
        cmds.deleteUI(ui_animHelpWindow)
        
    cmds.window(ui_animHelpWindow, s=True, width=500, height=500, menuBar=True, title="Help on Animation Export")
    cmds.paneLayout(configuration='horizontal4')
    cmds.scrollField(editable=False, wordWrap=True, text="Animation Export: \nAnimation export assumes single-level referencing with proper namesapce.\n\nActors: \nAll referenced characters with a origin joint tagged with the origin attribute will be listed in the Actor's field by their namespace. Please see the modeling help window for how to tage a character's origin with the origin attribute.\n\nExport Nodes:\nThe Export Nodes panel will fill in with export nodes connected to the origin of the selected actor from the Actor's field. Clicking on the New Export Node will create a new node. Each export node represents a seperate animation.\n\nExport:\nThe Export flag means the current export ndoe will be available for export. All nodes wihtout this checked will not be exported.\n\nMove to origin:\nNot yet supported\n\nSub Range:\nTurn this on to enable the sub-range option for the selected node. This will enable the Start Frame and End Frame fields where you can set the range for the specified animation. Otherwise, the animation will use the frame range of the file.\n\nExport File Name:\nClick on the Browse button to browse to where you want the file to go. The path will be project relative.\n\nExport Selected Animation:\nClick this button to export the animation selected in Export Nodes\n\nExport All Animations For Selected Character:\nClick this button to export all animations for the selected actor in the Actors filed. This flag will ignore what is selected in Export Nodes and export from all found nodes for the character\n\nExport All Animations:\nClick this button to export all animations for all characters. All selections will be ignored" )		
    
    cmds.showWindow(ui_animHelpWindow)


def FBXExporter_ModelHelpWindow():
    ui_modelHelpWindow = "ui_FBXExporter_ModelHelpWindow"
    if cmds.window(ui_modelHelpWindow, exists=True):
        cmds.deleteUI(ui_modelHelpWindow)
        
    cmds.window(ui_modelHelpWindow, s=True, width=500, height=500, menuBar=True, title="Help on Model Export")
    cmds.paneLayout(configuration='horizontal4')
    cmds.scrollField(editable=False, wordWrap=True, text="Model Export: \nModel exporter assumes one skeleton for export. Referencing for model export is not supported\n\nRoot Joints: \nPanel will list all the joints tagged with the \"origin\" attribute. If no joint is tagged with the attribute, it will list all joints in the scene and turn red. Select the root joint and click the Tag as Origin button.\n\nExport Nodes:\nThe Export Nodes panel will fill in with export nodes connected to the origin of the selected actor from the Actor's field. Clicking on the New Export Node will create a new node. Each export node represents a seperate character export (for example, seperate LOD's).\n\nMeshes:\nThe Meshes panel shows all the geometry associated with the selected export node. This can be used if you have mesh variations skinned to the same rig or LOD's.\n\nExport File Name:\nClick on the Browse button to browse to where you want the file to go. The path will be project relative.\n\nExport Selected Character:\nClick this button to export the character selected in Export Nodes\n\nExport All Characters:\nClick this button to export all character definitions for the skeleton. All selections will be ignored" )

    cmds.showWindow(ui_modelHelpWindow)



#
# Main UI
#

def FBXExporter_UI():
    #create main window
    ui_mainWindow = "ui_FBXExporter_window"
    if cmds.window(ui_mainWindow, exists=True):
        cmds.deleteUI(ui_mainWindow)

    cmds.window(ui_mainWindow, s=True, width=1000, height=700, menuBar=True, title="FBX Exporter")

    #create menu bar commands
    ui_windowEditMenu = "ui_FBXExporter_window_editMenu"
    ui_windowHelpMenu = "ui_FBXExporter_window_helpMenu"

    cmds.menu(ui_windowEditMenu, label="Edit")
    cmds.menuItem(label="Save Settings", parent=ui_windowEditMenu)
    cmds.menuItem(label="Reset Settings", parent=ui_windowEditMenu)

    cmds.menu(ui_windowHelpMenu, label="Help")
    cmds.menuItem(label="Help on Animation Export", command = "import FBXAnimationExporter as FBX\nFBX.FBXExporter_AnimationHelpWindow()", parent=ui_windowHelpMenu)
    cmds.menuItem(label="Help on Model Export", command = "import FBXAnimationExporter as FBX\nFBX.FBXExporter_ModelHelpWindow()", parent=ui_windowHelpMenu)

    #create main tab layout
    ui_windowMainForm = "ui_FBXExporter_window_mainForm"
    ui_windowTabLayout = "ui_FBXExporter_window_tabLayout"

    cmds.formLayout(ui_windowMainForm)
    cmds.tabLayout(ui_windowTabLayout, innerMarginWidth=5, innerMarginHeight=5)
    cmds.formLayout(ui_windowMainForm, edit=True, attachForm=[(ui_windowTabLayout, 'top', 0), (ui_windowTabLayout, 'left', 0), (ui_windowTabLayout, 'bottom', 0), (ui_windowTabLayout, 'right', 0)])

    #create animation ui elements
    ui_windowAnimFrameLayout = "ui_FBXExporter_window_animationFrameLayout"
    ui_windowAnimFormLayout = "ui_FBXExporter_window_animationFormLayout"

    cmds.frameLayout(ui_windowAnimFrameLayout, collapsable=False, label="", borderVisible=False, parent=ui_windowTabLayout)
    cmds.formLayout(ui_windowAnimFormLayout, numberOfDivisions=100, parent=ui_windowAnimFrameLayout)

    ui_windowAnimActorsTextScrollList = "ui_FBXExporter_window_animationActorsTextScrollList"
    ui_windowAnimExportNodesTextScrollList = "ui_FBXExporter_window_animationExportNodesTextScrollList"
    ui_windowAnimNewExportNodeButton = "ui_FBXExporter_window_animationNewExportNodeButton"
    ui_windowAnimExportCheckBoxGrp = "ui_FBXExporter_window_animationExportCheckBoxGrp"
    ui_windowAnimZeroOriginCheckBoxGrp = "ui_FBXExporter_window_animationZeroOriginCheckBoxGrp"
    ui_windowAnimZeroOriginMotionCheckBoxGrp = "ui_FBXExporter_window_animationZeroOriginMotionCheckBoxGrp"
    ui_windowAnimSubRangeCheckBoxGrp = "ui_FBXExporter_window_animationSubRangeCheckBoxGrp"
    ui_windowAnimStartFrameFloatFieldGrp = "ui_FBXExporter_window_animationStartFrameFloatFieldGrp"
    ui_windowAnimEndFrameFloatFieldGrp = "ui_FBXExporter_window_animationEndFrameFloatFieldGrp"
    ui_windowAnimExportFileNameTextFieldButtonGrp = "ui_FBXExporter_window_animationExportFileNameTextFieldButtonGrp"
    ui_windowAnimRecordAnimLayersButton = "ui_FBXExporter_window_animationRecordAnimLayersButton"
    ui_windowAnimPreviewAnimLayersButton = "ui_FBXExporter_window_animationPreviewAnimLayersButton"
    ui_windowAnimClearAnimLayersButton = "ui_FBXExporter_window_animationClearAnimLayersButton"
    ui_windowAnimActorText = "ui_FBXExporter_window_animationActorText"
    ui_windowAnimExportNodesText = "ui_FBXExporter_window_animationExportNodesText"
    ui_windowAnimExportSelectedAnimButton = "ui_FBXExporter_window_animationExportSelectedAnimationButton"
    ui_windowAnimExportAllAnimationsForSelectedChrButton = "ui_FBXExporter_window_animationExportAllAnimationsForSelectedCharacterButton"
    ui_windowAnimExportAllAnimsButton = "ui_FBXExporter_window_animationExportAllAnimationsButton"
    
    cmds.textScrollList(ui_windowAnimActorsTextScrollList, width=250, height=325, numberOfRows=18, allowMultiSelection=False, parent=ui_windowAnimFormLayout)
    cmds.textScrollList(ui_windowAnimExportNodesTextScrollList, width=250, height=325, numberOfRows=18, allowMultiSelection=False, parent=ui_windowAnimFormLayout)
    cmds.button(ui_windowAnimNewExportNodeButton, width=250, height=50, label="New Export Node", parent=ui_windowAnimFormLayout)
    cmds.checkBoxGrp(ui_windowAnimExportCheckBoxGrp, numberOfCheckBoxes=1, label="Export", columnWidth2=[85, 70], enable=False, parent=ui_windowAnimFormLayout)
    cmds.checkBoxGrp(ui_windowAnimZeroOriginCheckBoxGrp, numberOfCheckBoxes=1, label="Move To Origin", columnWidth2=[85, 70], enable=False, parent=ui_windowAnimFormLayout)
    cmds.checkBoxGrp(ui_windowAnimZeroOriginMotionCheckBoxGrp, numberOfCheckBoxes=1, label="Zero Motion on Origin", columnWidth2=[120, 70], enable=False, parent=ui_windowAnimFormLayout)
    cmds.checkBoxGrp(ui_windowAnimSubRangeCheckBoxGrp, numberOfCheckBoxes=1, label="Use Sub Range", columnWidth2=[85, 70], enable=False, parent=ui_windowAnimFormLayout)
    cmds.floatFieldGrp(ui_windowAnimStartFrameFloatFieldGrp, numberOfFields=1, label="Start Frame", columnWidth2=[75,70], enable=False, value1=0.0, parent=ui_windowAnimFormLayout)
    cmds.floatFieldGrp(ui_windowAnimEndFrameFloatFieldGrp, numberOfFields=1, label="End Frame", columnWidth2=[75,70], enable=False, value1=1.0, parent=ui_windowAnimFormLayout)
    cmds.textFieldButtonGrp(ui_windowAnimExportFileNameTextFieldButtonGrp, label="Export File Name", columnWidth3=[100,300,30], enable=False, text="", buttonLabel="Browse", parent=ui_windowAnimFormLayout)
    cmds.button(ui_windowAnimRecordAnimLayersButton, enable=False,width=150, height=50, label="Record Anim Layers", backgroundColor=[1, .25, .25], parent=ui_windowAnimFormLayout)
    cmds.button(ui_windowAnimPreviewAnimLayersButton, enable=False, width=250, height=50, label="Preview Anim Layers", parent=ui_windowAnimFormLayout)
    cmds.button(ui_windowAnimClearAnimLayersButton, enable=False, width=250, height=50, label="Clear Anim Layers", parent=ui_windowAnimFormLayout)
    cmds.text(ui_windowAnimActorText, label="Actors", parent=ui_windowAnimFormLayout)
    cmds.text(ui_windowAnimExportNodesText, label="Export Nodes", parent=ui_windowAnimFormLayout)
    cmds.button(ui_windowAnimExportSelectedAnimButton, width=300, height=50, label="Export Selected Animation", parent=ui_windowAnimFormLayout)
    cmds.button(ui_windowAnimExportAllAnimationsForSelectedChrButton, width=300, height=50, label="Export All Animation For Selected Character", parent=ui_windowAnimFormLayout)
    cmds.button(ui_windowAnimExportAllAnimsButton, width=300, height=50, label="Export All Animation", parent=ui_windowAnimFormLayout)

    ui_windowAnimExportNodesPopupMenu = "ui_FBXExporter_window_animationExportNodesPopupMenu"

    cmds.popupMenu(ui_windowAnimExportNodesPopupMenu, button=3, parent=ui_windowAnimExportNodesTextScrollList)
    cmds.menuItem("ui_FBXExporter_window_animationSelectNodeMenuItem", label="Select", parent=ui_windowAnimExportNodesPopupMenu )
    cmds.menuItem("ui_FBXExporter_window_animationRenameNodeMenuItem", label="Rename", parent=ui_windowAnimExportNodesPopupMenu )
    cmds.menuItem("ui_FBXExporter_window_animationDeleteNodeMenuItem", label="Delete", parent=ui_windowAnimExportNodesPopupMenu )

    #crete model ui elements
    ui_windowModelFrameLayout = "ui_FBXExporter_window_modelFrameLayout"
    ui_windowModelFormLayout = "ui_FBXExporter_window_modelFormLayout"
    
    cmds.frameLayout(ui_windowModelFrameLayout, collapsable=False, label="", borderVisible=False, parent=ui_windowTabLayout)
    cmds.formLayout(ui_windowModelFormLayout, numberOfDivisions=100, parent=ui_windowModelFrameLayout)
    
    ui_winModExpChkBoxGrp = "ui_FBXExporter_window_modelExportCheckBoxGrp"
    ui_winModOriText = "ui_FBXExporter_window_modelOriginText"
    ui_winModExpNodesText = "ui_FBXExporter_window_modelExportNodesText"
    ui_winModMeshText = "ui_FBXExporter_window_modelsMeshesText"
    ui_winModOriTextScrollList = "ui_FBXExporter_window_modelsOriginTextScrollList"
    ui_winModExpNodesTextScrollList = "ui_FBXExporter_window_modelsExportNodesTextScrollList"
    ui_winModGeomTextScrollList = "ui_FBXExporter_window_modelsGeomTextScrollList"
    ui_winModTagAsOriBtn = "ui_FBXExporter_window_modelTagAsOriginButton"
    ui_winModNewExpNodeBtn = "ui_FBXExporter_window_modelNewExportNodeButton"
    ui_winModAddRemoveMeshBtn = "ui_FBXExporter_window_modelAddRemoveMeshesButton"
    ui_winModExpFileNameTextFieldBtnGrp = "ui_FBXExporter_window_modelExportFileNameTextFieldButtonGrp"
    ui_winModExpMeshBtn = "ui_FBXExporter_window_modelExportMeshButton"
    ui_winModExpAllMeshsBtn = "ui_FBXExporter_window_modelExportAllMeshesButton"

    cmds.checkBoxGrp(ui_winModExpChkBoxGrp, numberOfCheckBoxes=1, label="Export", cc="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_UpdateExportNodeFromModelSettings()", columnWidth2=[85,70], enable=False, parent=ui_windowModelFormLayout)
    cmds.text(ui_winModOriText, label="Root Joints", parent=ui_windowModelFormLayout)
    cmds.text(ui_winModExpNodesText, label="Export Nodes", parent=ui_windowModelFormLayout)
    cmds.text(ui_winModMeshText, label="Meshes", parent=ui_windowModelFormLayout)
    cmds.textScrollList(ui_winModOriTextScrollList, width=175, height=220, numberOfRows=18, allowMultiSelection=False, sc="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_PopulateModelsExportNodesPanel()", parent=ui_windowModelFormLayout)
    cmds.textScrollList(ui_winModExpNodesTextScrollList, width=175, height=220,  numberOfRows=18, allowMultiSelection=False, sc="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_PopulateGeomPanel()\nFBX.FBXExporterUI_UpdateModelExportSettings()", parent=ui_windowModelFormLayout)
    cmds.textScrollList(ui_winModGeomTextScrollList, width=175, height=220,  numberOfRows=18, allowMultiSelection=True,  parent=ui_windowModelFormLayout)
    cmds.button(ui_winModTagAsOriBtn, width=175, height=50, label="Tag as Origin", command="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_ModelTagForOrigin()", parent=ui_windowModelFormLayout)
    cmds.button(ui_winModNewExpNodeBtn, width=175, height=50, label="New Export Node", command="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_ModelCreateNewExportNode()", parent=ui_windowModelFormLayout)
    cmds.button(ui_winModAddRemoveMeshBtn, width=175, height=50, label="Add / Remove Meshes", command="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_ModelAddRemoveMeshes()", parent=ui_windowModelFormLayout)
    cmds.textFieldButtonGrp(ui_winModExpFileNameTextFieldBtnGrp, label='Export File Name', bc="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_BrowseExportFilename(2)", cc="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_UpdateExportNodeFromAnimationSettings()", columnWidth3=[100,300,30], enable=False, text='', buttonLabel='Browse', parent=ui_windowModelFormLayout )
    cmds.button(ui_winModExpMeshBtn, width=250, height=50, label="Export Selected Character", command="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_ModelExportSelectedCharacter()", parent=ui_windowModelFormLayout)
    cmds.button(ui_winModExpAllMeshsBtn, width=250, height=50, label="Export All Characters", command="import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_ModelExportAllCharacters()", parent=ui_windowModelFormLayout)

    ui_windowModelExportNodesPopupMenu = "ui_FBXExporter_window_modelExportNodesPopupMenu"

    cmds.popupMenu(ui_windowModelExportNodesPopupMenu, button=3, parent=ui_winModExpNodesTextScrollList)
    cmds.menuItem("ui_FBXExporter_window_modelSelectNodeMenuItem", label="Select", parent=ui_windowModelExportNodesPopupMenu )
    cmds.menuItem("ui_FBXExporter_window_modelRenameNodeMenuItem", label="Rename", parent=ui_windowModelExportNodesPopupMenu )
    cmds.menuItem("ui_FBXExporter_window_modelDeleteNodeMenuItem", label="Delete", parent=ui_windowModelExportNodesPopupMenu )

    #set up tabs
    cmds.tabLayout(ui_windowTabLayout, edit=True, tabLabel=((ui_windowAnimFrameLayout, "Animation"),(ui_windowModelFrameLayout, "Model")))


    #set up animation form layout
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachForm=[(ui_windowAnimActorText, 'top', 5), (ui_windowAnimActorText, 'left', 5), (ui_windowAnimActorsTextScrollList, 'left', 5), (ui_windowAnimExportNodesText, 'top', 5), (ui_windowAnimExportCheckBoxGrp, 'top', 25), (ui_windowAnimZeroOriginCheckBoxGrp, 'top', 25), (ui_windowAnimZeroOriginMotionCheckBoxGrp, 'top', 25), (ui_windowAnimExportFileNameTextFieldButtonGrp, 'right', 5)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimExportNodesTextScrollList, 'left', 5, ui_windowAnimActorsTextScrollList), (ui_windowAnimExportCheckBoxGrp, 'left', 20, ui_windowAnimExportNodesTextScrollList), (ui_windowAnimZeroOriginCheckBoxGrp, 'left', 5, ui_windowAnimExportCheckBoxGrp), (ui_windowAnimZeroOriginMotionCheckBoxGrp, 'left', 5, ui_windowAnimZeroOriginCheckBoxGrp)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimSubRangeCheckBoxGrp, 'left', 20, ui_windowAnimExportNodesTextScrollList), (ui_windowAnimSubRangeCheckBoxGrp, 'top', 5, ui_windowAnimZeroOriginCheckBoxGrp)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimStartFrameFloatFieldGrp, 'left', 30, ui_windowAnimExportNodesTextScrollList), (ui_windowAnimStartFrameFloatFieldGrp, 'top', 5, ui_windowAnimSubRangeCheckBoxGrp)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimEndFrameFloatFieldGrp, 'left', 1, ui_windowAnimStartFrameFloatFieldGrp), (ui_windowAnimEndFrameFloatFieldGrp, 'top', 5, ui_windowAnimSubRangeCheckBoxGrp)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimExportFileNameTextFieldButtonGrp, 'left', 5, ui_windowAnimExportNodesTextScrollList), (ui_windowAnimExportFileNameTextFieldButtonGrp, 'top', 5, ui_windowAnimStartFrameFloatFieldGrp)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimNewExportNodeButton, 'left', 5, ui_windowAnimActorsTextScrollList), (ui_windowAnimNewExportNodeButton, 'top', 5, ui_windowAnimExportNodesTextScrollList)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimActorsTextScrollList, 'top', 5, ui_windowAnimActorText), (ui_windowAnimExportNodesTextScrollList, 'top', 5, ui_windowAnimExportNodesText), (ui_windowAnimExportNodesText, 'left', 225, ui_windowAnimActorText)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimRecordAnimLayersButton, 'top', 10, ui_windowAnimExportFileNameTextFieldButtonGrp), (ui_windowAnimPreviewAnimLayersButton, 'top', 10, ui_windowAnimExportFileNameTextFieldButtonGrp), (ui_windowAnimClearAnimLayersButton, 'top', 10, ui_windowAnimExportFileNameTextFieldButtonGrp)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimRecordAnimLayersButton, 'left', 10, ui_windowAnimExportNodesTextScrollList), (ui_windowAnimPreviewAnimLayersButton, 'left', 10, ui_windowAnimRecordAnimLayersButton), (ui_windowAnimClearAnimLayersButton, 'left', 10, ui_windowAnimPreviewAnimLayersButton)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimExportSelectedAnimButton, 'top', 10, ui_windowAnimRecordAnimLayersButton), (ui_windowAnimExportAllAnimationsForSelectedChrButton, 'top', 10, ui_windowAnimExportSelectedAnimButton), (ui_windowAnimExportAllAnimsButton, 'top', 10,ui_windowAnimExportAllAnimationsForSelectedChrButton)])
    cmds.formLayout(ui_windowAnimFormLayout, edit=True, attachControl=[(ui_windowAnimExportSelectedAnimButton, 'left', 100, ui_windowAnimExportNodesTextScrollList), (ui_windowAnimExportAllAnimationsForSelectedChrButton, 'left', 100, ui_windowAnimExportNodesTextScrollList), (ui_windowAnimExportAllAnimsButton, 'left', 100, ui_windowAnimExportNodesTextScrollList)])

    #set up model form layout
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachForm=[(ui_winModOriText, 'top', 5), (ui_winModOriText, 'left', 5), (ui_winModOriTextScrollList, 'left', 5), (ui_winModExpNodesText, 'top', 5), (ui_winModMeshText, 'top', 5), (ui_winModExpChkBoxGrp, 'top', 25), (ui_winModTagAsOriBtn, 'left', 5)])
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachControl=[(ui_winModExpNodesText, 'left', 125, ui_winModOriText), (ui_winModMeshText, 'left', 120, ui_winModExpNodesText)])
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachControl=[(ui_winModOriTextScrollList, 'top', 5, ui_winModOriText),(ui_winModExpNodesTextScrollList, 'top', 5, ui_winModExpNodesText), (ui_winModGeomTextScrollList, 'top', 5, ui_winModMeshText)])
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachControl=[(ui_winModExpNodesTextScrollList, 'left', 5, ui_winModOriTextScrollList), (ui_winModGeomTextScrollList, 'left', 5, ui_winModExpNodesTextScrollList)])
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachControl=[(ui_winModNewExpNodeBtn, 'left', 5, ui_winModOriTextScrollList), (ui_winModNewExpNodeBtn, 'top', 5, ui_winModExpNodesTextScrollList)])
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachControl=[(ui_winModExpFileNameTextFieldBtnGrp, 'left', 5, ui_winModGeomTextScrollList),(ui_winModTagAsOriBtn, 'top', 5, ui_winModOriTextScrollList)])
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachControl=[(ui_winModExpMeshBtn, 'top', 15, ui_winModExpFileNameTextFieldBtnGrp),(ui_winModExpMeshBtn, 'left', 125, ui_winModGeomTextScrollList)])
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachControl=[(ui_winModAddRemoveMeshBtn, 'top', 5, ui_winModGeomTextScrollList),(ui_winModAddRemoveMeshBtn, 'left', 5, ui_winModNewExpNodeBtn)])
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachControl=[(ui_winModExpAllMeshsBtn, 'top', 5, ui_winModExpMeshBtn),(ui_winModExpAllMeshsBtn, 'left', 125, ui_winModGeomTextScrollList)])
    cmds.formLayout(ui_windowModelFormLayout, edit= True, attachControl=[(ui_winModExpFileNameTextFieldBtnGrp, 'top', 5, ui_winModExpChkBoxGrp),(ui_winModExpChkBoxGrp, 'left', 125, ui_winModGeomTextScrollList)])


    # populate ui
    FBXExporterUI_PopulateModelRootJointsPanel(ui_winModOriTextScrollList)
    FBXExporterUI_PopulateAnimationActorPanel(ui_windowAnimActorsTextScrollList)

    # scriptJob to refresh ui
    cmds.scriptJob(parent=ui_mainWindow, e=["PostSceneRead", "import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_PopulateModelRootJointsPanel()"])
    cmds.scriptJob(parent=ui_mainWindow, e=["PostSceneRead", "import FBXAnimationExporter as FBX\nFBX.FBXExporterUI_PopulateAniamtionActorPanel()"])




    cmds.showWindow(ui_mainWindow)