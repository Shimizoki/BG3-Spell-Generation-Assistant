from typing import Dict

import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

import os

from utils import utils
from widgets import widgets
import models
import writers
from data import BG3Database

# Main Frame
class FolderStructure(tk.Frame):
    ATLAS_BASE_PATH = os.path.join("Assets", "Textures", "Icons", "Icons_" + "{0}" + ".dds")
    ATLAS_PATH = os.path.join("Public", "{0}", ATLAS_BASE_PATH)
    CONTROLLER_ICON_PATH = os.path.join("Public", "Game", "GUI", "Assets", "ControllerUIIcons", "skills_png", "{0}" + ".DDS")
    TOOLTIP_ICON_PATH = os.path.join("Public", "Game", "GUI", "Assets", "Tooltips", "Icons", "{0}" + ".DDS")

    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.spells: Dict[str,models.Spell] = {}

        top_frame = tk.Frame(master)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Mod Container for Information relevant to the whole mod
        self.modWidget = widgets.ModWidget(top_frame)
        self.modWidget.pack(side=tk.TOP, fill=tk.X, expand=True, padx=10)
        ttk.Separator(self.modWidget, orient="horizontal").pack( fill=tk.X, expand=1, pady=4)

        center_frame = tk.Frame(master, background="green")
        center_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(center_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        add_remove_spell_frame = tk.Frame(self.left_frame)
        add_remove_spell_frame.pack(side=tk.TOP, fill=tk.X)

        button_RemoveSpell = tk.Button(add_remove_spell_frame, text="-", command=self.on_remove_spell_click)
        button_RemoveSpell.pack(side=tk.LEFT, fill=tk.X, expand=True)
        button_AddSpell = tk.Button(add_remove_spell_frame, text="+", command=self.on_add_spell_click)
        button_AddSpell.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.spellTabWidget = widgets.ReorderableList(self.left_frame, width=150, cellHeight=20)
        self.spellTabWidget.pack(fill=tk.Y, expand=True)

        self.on_add_spell_click()        

        # Spell Container for Information relevant to the a single spell
        self.spellWidget = widgets.SpellWidget(center_frame)
        self.spellWidget.fromSpell(self.spells[next(iter(self.spells.keys()))])
        self.spellWidget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True) 
        
        # Bottom Button for Generation
        bottom_frame = tk.Frame(master, background="green")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        button_Generate = tk.Button(bottom_frame, text="Generate Files", command=self.on_Generate_Click)
        button_Generate.pack()

    def on_reorderable_click(self, value: models.Spell) -> None:
        self.spellWidget.save()
        self.spellTabWidget.renameLables({uuid : spell.getName() for uuid, spell in self.spells.items()}) 
        self.spellWidget.fromSpell(value)

    def on_add_spell_click(self) -> None:
        spell = models.Spell(uuid=utils.Generate_UUID())
        spell.id = f"Default_Spell_{len(self.spells)}"
        spell.setName(f"Spell {len(self.spells)}")
        self.spells[spell.uuid] = spell
        
        widget = tk.Label(self.left_frame, text=f"{spell.getName()}", width=16, padx=4)
        self.spellTabWidget.add_widget(widget, ref_uuid=spell.uuid, callback=lambda s=spell: self.on_reorderable_click(s))

    def on_remove_spell_click(self) -> None:
        if len(self.spells) > 1:
            uuid = self.spellWidget.ref_spell.uuid
            
            self.spellTabWidget.remove_widget(uuid=uuid)
            self.spells.pop(uuid)
            
            (_,nextSpell) = list(self.spells.items())[-1]
            self.spellWidget.fromSpell(nextSpell)
            
    # Create a button widget and define its click action
    def on_Generate_Click(self):
        
        # Parse UI
        modName = self.modWidget.Name
        modPath = self.modWidget.Path
        spellWidget = self.spellWidget
        spellWidget.save()

        spellTemplateFile = writers.SpellFile(fileName=f"{modName}_Spells")
        localizationFile = writers.LocalizationFile(fileName=modName)
        spellListCombinerFile = writers.SpellListCombinerFile()
        
        imageMover = writers.ImageMover()

        atlasFile = writers.AtlasFile(uuid=utils.Generate_UUID(), fileName=f"Icons_{modName}",atlasTemplate="templates/atlas_256.dds", iconSize=64, icons=[])
        atlasTemplateFile = writers.AtlasTemplateFile(fileName=atlasFile.fileName, path=self.ATLAS_BASE_PATH.format(modName), atlas=atlasFile, icons=[])
        mergedTemplateFile = writers.MergedFile(uuid=atlasFile.uuid, name=atlasFile.fileName, sourceFile=self.ATLAS_PATH.format(modName), template=f"Icons_{modName}")
               
        for data in self.spellTabWidget.widget_data:
            spell = self.spells[data["ref_uuid"]]
            
            spellTemplateFile.addSpell(spell)

            localizationFile.addElement(spell.name)
            localizationFile.addElement(spell.description)

            imageMover.addImage(models.PathVector(inPath=spell.controllerIcon, outPath=self.CONTROLLER_ICON_PATH.format(spell.id)))
            imageMover.addImage(models.PathVector(inPath=spell.tooltipIcon, outPath=self.TOOLTIP_ICON_PATH.format(spell.id)))

            atlasFile.addIcon(spell.controllerIcon)
            atlasTemplateFile.addIcon(spell.id)

            spellListCombinerFile.addElement(name=f"{spell.spellType}_{spell.id}", listUUIDs=spell.lists)

        # Do Exports to disc
        spellTemplateFile.export(os.path.join(modPath, modName, "Public", modName, "Stats", "Generated", "Data"))
        localizationFile.export(os.path.join(modPath, modName, "Localization", "English"))
        imageMover.export(os.path.join(modPath, modName))
        atlasTemplateFile.export(os.path.join(modPath, modName, "Public", modName, "GUI"))
        mergedTemplateFile.export(os.path.join(modPath, modName, "Public", modName, "Content", "UI", "[PAK]_UI"))
        spellListCombinerFile.export(os.path.join(modPath, modName, "Public", modName , "Lists"))

        atlasFile.export(os.path.join(modPath, modName, os.path.dirname(self.ATLAS_PATH.format(modName))))
        
        if not os.path.exists(os.path.join(modPath, modName, "Mods")):
            os.makedirs(os.path.join(modPath, modName, "Mods"))


# Create the main window
root = TkinterDnD.Tk()
root.title("BG3 Spell Maker")
root.minsize(800,400)

BG3Database.LoadData()
myapp = FolderStructure(root)

# Run the main event loop
root.mainloop()
