from xml.dom.minidom import parse
 
dom = parse("C:/Temp/test.xml")
 
 # visit every object node 
for node in dom.getElementsByTagName('object'): 
     
    # method 1: using keys
    attrs = node.attributes.keys()
    for a in attrs:
        pair = node.attributes[a]
        print (str(pair.name) + " = " + str(pair.value))
    print
     
    #method 2: by attribute name
"""        
    print str(node.getAttribute("name"))
    print str(node.getAttribute("translateX"))
    print str(node.getAttribute("translateY"))
    print str(node.getAttribute("translateZ"))
    print
"""