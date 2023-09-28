from typing import List
from typing import Dict

import xml.etree.ElementTree as ET
from PIL import Image
import os
import json
import shutil

import models
from utils import utils

# Writes the Localization to it's required mod location
class LocalizationFile:
    fileExtension: str = ".loca.xml"

    def __init__(self, fileName: str) -> None:
        self.fileName: str = fileName
        self.localizations: Dict[str, models.Localization] = {}

    def addElement(self, localization: models.Localization) -> None:
        self.localizations[localization.uuid] = localization

    def __str__(self) -> str:
        return str(ET.tostring(self.dump()))
    
    def dump(self) -> ET.Element:
        root = ET.Element("contentList")
        for (_,v) in self.localizations.items():
            root.append(v.toXML())
        
        return root

    def export(self, path: str) -> None:
        # Create the directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        tree = ET.ElementTree(self.dump())
        with open(os.path.join(path, self.fileName + self.fileExtension), "wb") as file:
            tree.write(file, encoding="utf-8")

# Writes the Spell template it's required mod location
class SpellFile:
    fileExtension: str = ".txt"

    def __init__(self, fileName: str) -> None:
        self.fileName: str = fileName
        self.spells: List[models.Spell] = [] 
    
    def addSpell(self, spell: models.Spell) -> None:
        self.spells.append(spell)
    
    def __str__(self) -> str:
        value = ""
        for s in self.spells:
            value += str(s) + "\n\n"

        return value
    
    def export(self, path: str) -> None:
        # Create the directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(path, self.fileName + self.fileExtension), "wb") as file:
            file.write(str(self).encode("utf-8"))

# Writes the SpellList Combiner to it's required mod location
class SpellListCombinerFile:
    fileExtension = ".lsj"

    def __init__(self) -> str:
        self.fileName: str = "SpellLists"
        self.lists: List[tuple[str, List[str]]] = []

    def addElement(self, name: str, listUUIDs: List[str]) -> None:
        self.lists.append((listUUIDs, name))
        
    def dump(self) -> str:
        root = []

        for e in self.lists:
            root.append(self.createNode(e[1], [], "", e[0]))

        return root

    def createNode(self, spellID: str, dependencyUUIDs: List[str], comment: str, spellListUUIDs: List[str]) -> dict:
        node = {}
        node["Depends"] = dependencyUUIDs
        node["SpellLists"] = []
        node["SpellLists"].append(self.createSpellList(spellID=spellID, comment=comment, spellListUUIDs=spellListUUIDs))
        
        return node

    def createSpellList(self, spellID: str, comment: str, spellListUUIDs: List[str]) -> dict:
        node = {}
        node["Comment"] = comment
        node["UUID"] = spellListUUIDs[0] if (len(spellListUUIDs) > 0) else ""
        node["Spells"] = spellID
        node["AdditionalSpellLists"] = spellListUUIDs[1:] if (len(spellListUUIDs) > 1) else []

        return node
    
    def __str__(self) -> str:
        return str(ET.tostring(self.dump(), encoding="utf-8"))
    
    def export(self, path: str) -> None:
        # Create the directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(path, self.fileName + self.fileExtension), "w", encoding="utf-8") as file:
            json.dump(self.dump(), file, indent=4)

# Moves images to their respective locations
class ImageMover:
    def __init__(self) -> None:
        self.imageViews: List[models.PathVector] = []

    def addImage(self, imageView:models.PathVector) -> None:
        self.imageViews.append(imageView)
    
    def export(self, modPath:str) -> None:
        for iv in self.imageViews:
            if iv.inPath:
                path = os.path.join(modPath, iv.outPath)

                # Create the directory if it doesn't exist
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                if os.path.exists(iv.inPath):
                    shutil.copy(iv.inPath, path)

# Writes the Merged file to it's required mod location
class MergedFile:
    fileExtension: str = ".lsf.lsx"

    def __init__(self, uuid, name, sourceFile, template) -> None:
        self.fileName: str = "_merged"
        self.uuid: str = uuid
        self.name: str = name
        self.sourceFile: str = sourceFile
        self.template: str = template

    def __str__(self) -> str:
        return str(ET.tostring(self.dump()))
    
    def dump(self) -> ET.Element:
        root = ET.Element("save")

        ET.SubElement(root, "version", attrib={"major":"4","minor":"0","revision":"6","build":"5","lslib_meta":"v1,bswap_guids"})

        p1   = ET.SubElement(root, "region", attrib={"id":"TextureBank"})
        p2   = ET.SubElement(p1, "node", attrib={"id":"TextureBank"})
        p3   = ET.SubElement(p2, "children")
        node = ET.SubElement(p3, "node", attrib={"id":"Resource"})
        
        node.append(self.createAttrib("ID", "FixedString", self.uuid))
        node.append(self.createAttrib("Localized", "bool", "False"))
        node.append(self.createAttrib("Name", "LSString", self.name))
        node.append(self.createAttrib("SRGB", "bool", "True"))
        node.append(self.createAttrib("SourceFile", "LSString", self.sourceFile))
        node.append(self.createAttrib("Streaming", "bool", "True"))
        node.append(self.createAttrib("Template", "FixedString", self.template))
        node.append(self.createAttrib("Type", "int32", "0"))
        node.append(self.createAttrib("_OriginalFileVersion_", "int64", "144115188075855873"))

        return root
    
    def createAttrib(self, id: str, dataType: str, value: str) -> ET.Element:
        return ET.Element("attribute", attrib={"id":id, "type":dataType, "value":value})
    
    def export(self, path: str) -> None:
        # Create the directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        tree = ET.ElementTree(self.dump())
        with open(os.path.join(path, self.fileName + self.fileExtension), "wb") as file:
            tree.write(file, encoding="utf-8")

# Creates and writes the Atlas to it's required mod location
class AtlasFile:
    fileExtension: str = ".dds"

    def __init__(self, uuid: str, fileName: str, atlasTemplate: str, iconSize: tuple[int,int], icons: List[str]) -> None:
        self.fileName: str = fileName
        self.uuid: str = uuid

        self.atlasTemplate: str = atlasTemplate
        self.size: tuple[int,int] = utils.Get_Image_Dims(atlasTemplate) or [2048,2048]
        self.iconSize: tuple[int,int] = (iconSize,iconSize)
        self.icons: List[str] = icons

    def addIcon(self, icon: str) -> None:
        self.icons.append(icon)

    def dump(self) -> Image:
        count = [int(self.size[0] / self.iconSize[0]),int(self.size[1] / self.iconSize[1])]
        x = 0
        y = 0
        
        tmp = Image.open(self.atlasTemplate)
        image = tmp.copy()
        tmp.close()

        for i,path in enumerate(self.icons):
            if i >= count[0]*count[1]:
                break

            if path and os.path.exists(path):
                with Image.open(path) as icon:
                    image.paste(icon, (x*self.iconSize[0],y*self.iconSize[1]))
            x += 1
            if x >= count[0]:
                x = 0
                y += 1
        return image
        
    def export(self, modPath: str) -> None:        
        # Create the directory if it doesn't exist
        if modPath and not os.path.exists(modPath):
            os.makedirs(modPath)

        self.dump().save(os.path.join(modPath, self.fileName+self.fileExtension))

# Writes the Atlas Template to it's required mod locatin
class AtlasTemplateFile:
    fileExtension: str = ".lsx"

    def __init__(self, fileName: str, path: str, atlas: AtlasFile, icons: [str]) -> None:
        self.fileName: str = fileName
        self.path: str = path

        self.atlas: AtlasFile = atlas
        self.icons: List[str] = icons


    def __str__(self) -> str:
        return str(ET.tostring(self.dump()))
    
    def addIcon(self, icon: str):
        self.icons.append(icon)

    def dump(self) -> ET.Element:
        root = ET.Element("save")

        ET.SubElement(root, "version", attrib={"major":"4","minor":"0","revision":"6","build":"5"})

        p1 = ET.SubElement(root, "region", attrib={"id":"IconUVList"})
        p2 = ET.SubElement(p1, "node", attrib={"id":"root"})
        p3 = ET.SubElement(p2, "children")

        count = [int(self.atlas.size[0] / self.atlas.iconSize[0]),int(self.atlas.size[1] / self.atlas.iconSize[1])]
        for x in range(count[0]):
            x_min = x / count[0]
            x_max = (x+1) / count[0]
            for y in range(count[1]):
                y_min = y / count[1]
                y_max = (y+1) / count[1]
                flat_idx = (x*count[1])+y
                name = self.icons[flat_idx] if (len(self.icons) > flat_idx) else ""
                p3.append(self.IconUVNode(name, y_min, y_max, x_min, x_max))

        root.append(self.createTextureInfo())

        return root
    
    def IconUVNode(self, name: str, u1: float, u2: float, v1: float, v2: float) -> ET.Element:
        root = ET.Element("node", attrib={"id":"IconUV"})

        root.append(self.createAttrib("MapKey", "FixedString", name))
        root.append(self.createAttrib("U1", "float", str(u1)))
        root.append(self.createAttrib("U2", "float", str(u2)))
        root.append(self.createAttrib("V1", "float", str(v1)))
        root.append(self.createAttrib("V2", "float", str(v2)))

        return root

    def createAttrib(self, id: str, dataType: str, value: str) -> ET.Element:
        return ET.Element("attribute", attrib={"id":id, "type":dataType, "value":value})
    
    def createTextureInfo(self) -> ET.Element:
        root = ET.Element("region", attrib={"id":"TextureAtlasInfo"})

        p1 = ET.SubElement(root, "node", attrib={"id":"root"})
        p2 = ET.SubElement(p1, "children")
        
        (w,h) = self.atlas.iconSize
        iconSize = ET.SubElement(p2, "node", attrib={"id":"TextureAtlasIconSize"})
        iconSize.append(self.createAttrib("Height", "int32", str(h)))
        iconSize.append(self.createAttrib("Width", "int32", str(w)))

        atlasPath = ET.SubElement(p2, "node", attrib={"id":"TextureAtlasPath"})
        atlasPath.append(self.createAttrib("Path", "LSString", self.path))
        atlasPath.append(self.createAttrib("UUID", "FixedString", self.atlas.uuid))

        (w,h) = self.atlas.size
        atlasSize = ET.SubElement(p2, "node", attrib={"id":"TextureAtlasTextureSize"})
        atlasSize.append(self.createAttrib("Height", "int32", str(h)))
        atlasSize.append(self.createAttrib("Width", "int32", str(w)))

        return root

    def export(self, path: str) -> None:
        # Create the directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        tree = ET.ElementTree(self.dump())
        with open(os.path.join(path, self.fileName + self.fileExtension), "wb") as file:
            tree.write(file, encoding="utf-8")


