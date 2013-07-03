import maya.cmds as cmds

class Renamer():
    def __init__(self):
        window_name = "renamerWindow"
        window_title = "Renamer"
        
        if cmds.window(window_name, q=True, exists=True):
        	cmds.deleteUI(window_name)
        	
        my_window = cmds.window(window_name, title=window_title)
        
        main_layout = cmds.columnLayout(adj=True)
        
        self.find_box = cmds.textFieldButtonGrp(label="Find", text="", adj=2, buttonLabel="Select", cw=[1,50], bc=self.find_matches)
        self.replace_box = cmds.textFieldButtonGrp(label="Replace", text="", adj=2, buttonLabel="Replace", cw=[1,50], bc=self.replace)
        self.prefix_box = cmds.textFieldButtonGrp(label="Prefix", text="", adj=2, buttonLabel="Add", cw=[1,50], bc=self.add_prefix)
        self.suffix_box = cmds.textFieldButtonGrp(label="Suffix", text="", adj=2, buttonLabel="Add", cw=[1,50], bc=self.add_suffix)
        
        cmds.showWindow(my_window)
        
    def find_matches(self):
        find_string = cmds.textFieldButtonGrp(self.find_box, q=True, text=True)
        matches = cmds.ls("*" + find_string + "*", type="transform")
        if matches:
            cmds.select(matches, r=True)
        else:
            cmds.select(cl=True)
        
    def add_prefix(self):
        prefix = cmds.textFieldButtonGrp(self.prefix_box, q=True, text=True)
        selection = cmds.ls(sl=True)
        for sel in selection:
            new_name = prefix + sel
            print "Renaming", sel, ">", new_name
            cmds.rename(sel, new_name)

    def add_suffix(self):
        suffix = cmds.textFieldButtonGrp(self.suffix_box, q=True, text=True)
        selection = cmds.ls(sl=True)
        for sel in selection:
            new_name = sel + suffix
            print "Renaming", sel, ">", new_name
            cmds.rename(sel, new_name)
            
    def replace(self):
        find_string = cmds.textFieldButtonGrp(self.find_box, q=True, text=True)
        replace_string = cmds.textFieldButtonGrp(self.replace_box, q=True, text=True)
        matches = cmds.ls("*" + find_string + "*", type="transform")
        
        selection = cmds.ls(sl=True)
        for sel in selection:
            new_name = sel.replace(find_string, replace_string)
            print "Replacing", sel, ">", new_name
            cmds.rename(sel, new_name)
        

Renamer()