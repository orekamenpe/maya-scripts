from xml.dom.minidom import Document
import maya.cmds as cmds
 
doc = Document()
 
root_node = doc.createElement("scene")
doc.appendChild(root_node)
 
# Selection: 
# grab all selected objects
#selection = cmds.ls(sl=True)
 
# grab all visible objects, which type is transform
selection = cmds.ls(type="transform", v=True )
 
for object in selection:
     
    # create object element
    object_node = doc.createElement("object")
    root_node.appendChild(object_node)
     
    # BEWARE: after freeze transformations the translate is a bit tricky
    #object_translation = cmds.getAttr(object + ".translate")[0]
    object_translation = cmds.xform(object, query = True, worldSpace = True, rotatePivot = True) 
     
    # set attributes
    object_node.setAttribute("name", str(object))
    object_node.setAttribute("translateX", str(object_translation[0]))
    object_node.setAttribute("translateY", str(object_translation[1]))
    object_node.setAttribute("translateZ", str(object_translation[2]))
     
 
xml_file = open("C:/Temp/test.xml", "w")
xml_file.write(doc.toprettyxml())
xml_file.close()
 
print
print doc.toprettyxml()