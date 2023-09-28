from typing import List, Dict, Callable

import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os

import data as data
from utils import utils
import models

from data import BG3Database

# A drag and drop image frame that accepts DDS files
class DnDImage(tk.Frame):
    def __init__(self, master=None, **kwargs) -> None:
        dropEnabled: bool = kwargs.pop("enabled")
        text: str = kwargs.pop("label")
        super().__init__(master, **kwargs, relief="solid", borderwidth=1)

        self.path: str = ""

        # Create a Label for displaying the image
        self.data = ttk.Label(self, text=text, anchor="center", justify="center")
        self.data.pack(fill="both", expand=1)
        
        if dropEnabled:
            self.data.drop_target_register(DND_FILES)
            self.data.dnd_bind('<<Drop>>', self.on_drop)

        self.show()
    
    def show(self) -> None:
        self.pack_propagate(0)

    def hide(self) -> None:
        self.pack_forget()

    # Function to handle image drop
    def on_drop(self, event) -> None:
        path = event.data
        if path.lower().endswith(('.dds', '.DDS')):
            self.display_image(path)

    def display_image(self, path: str) -> None:
        if path and os.path.exists(path):
            image = Image.open(path)

            # Resize the image
            image = utils.Resize_Image(image, 64, 64)

            # Display the image in a Label
            photo = ImageTk.PhotoImage(image)
            self.data.config(image=photo)
            self.data.photo = photo
            self.path = path
        else:
            # Display the image in a Label
            self.data.config(image=None)
            self.data.photo = None
            self.path = None

# A labeled Drag and Drop image frame
class IconWidget(tk.Frame):
    def __init__(self, master=None, **kwargs) -> None:
        text: str = kwargs.pop("label")
        super().__init__(master, **kwargs)

        label = tk.Label(self, text=text)
        label.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.data = DnDImage(self, enabled=True, width=64, height=64, label="Drop DDS\nHere")
        self.data.pack(side=tk.TOP)

        self.show()
        
    def show(self) -> None:
        self.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def hide(self) -> None:
        self.pack_forget()

# A labeled combo box
class ComboWidget(tk.Frame):
    def __init__(self, master=None, **kwargs) -> None:
        text: str = utils.PopKwArgs(kwargs,"label", "")
        labelWidth: str = utils.PopKwArgs(kwargs,"labelWidth", 14)
        value: List[str] = utils.PopKwArgs(kwargs,"value", [])
        super().__init__(master, **kwargs)

        label = tk.Label(self, text=text, width=labelWidth, anchor=tk.E, padx=4)
        label.pack(side=tk.LEFT)

        self.data = ttk.Combobox(self, values=value)
        self.data.set(utils.GetFirstIn(value,""))
        self.data.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.show()
    
    def show(self) -> None:
        self.pack(fill=tk.X, expand=True, pady=2)

    def hide(self) -> None:
        self.pack_forget()

# A labeled text entry widget
class EntryWidget(tk.Frame):
    def __init__(self, master=None, **kwargs) -> None:
        text: str = utils.PopKwArgs(kwargs,"label", "")
        labelWidth: str = utils.PopKwArgs(kwargs,"labelWidth", 14)
        value: List[str] = utils.PopKwArgs(kwargs,"value", [])
        super().__init__(master, **kwargs)

        label = tk.Label(self, text=text, width=labelWidth, anchor=tk.E, padx=4)
        label.pack(side=tk.LEFT)

        self.data = tk.Entry(self, font=('calibre',10,'normal'))
        self.data.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.data.insert(0, value)

        self.show()
        
    def show(self) -> None:
        self.pack(fill=tk.X, expand=True, pady=2)

    def hide(self) -> None:
        self.pack_forget()

# A widget containing entry fields relevant to the mod as a whole
class ModWidget(tk.Frame):
    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self._Name = EntryWidget(self, label="Mod Name:", labelWidth=10, value="Default_Mod_Name")
        self._Path = EntryWidget(self, label="Mod Path:", labelWidth=10, value="Default_Mod_Path")

    @property
    def Name(self) -> str:
        return self._Name.data.get()
    
    @property
    def Path(self) -> str:
        return self._Path.data.get()

# A widget containing a list of checkboxes allowing multi-select of spell lists to which to add the selected spell  
class SpellListWidget(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        label = tk.Label(self, text="Spell Lists")
        label.pack(side=tk.TOP)

        # Create a canvas to hold the frame with checkboxes
        left_frame = tk.Frame(self, relief="solid", borderwidth=1, takefocus=False)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)        

        # Create a canvas to hold the frame with checkboxes
        canvas = tk.Canvas(left_frame, width=200, relief="sunken", highlightthickness=0, takefocus=False)
        canvas.pack(fill=tk.BOTH, expand=True)

        # Create a frame inside the canvas
        canvas_frame = tk.Frame(canvas, takefocus=False)
        canvas.create_window((0, 0), window=canvas_frame, anchor=tk.NW)

        # Create checkboxes in the frame
        self._SpellLists: List[tuple[str,tk.IntVar]] = []
        for (k,v) in data.spellLists.items():
            var = tk.IntVar()
            checkbox = ttk.Checkbutton(canvas_frame, text=f"{k}", variable=var, onvalue=1, offvalue=0, takefocus=False)
            checkbox.pack(fill=tk.X)
            self._SpellLists.append((v,var))
        
        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Update the canvas scrolling region
        canvas_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    @property
    def SpellLists(self):
        lists = []
        for (uuid, var) in self._SpellLists:
            if var.get():
                lists.append(uuid)
                
        return lists

# A widget containing a list of data entry fields to populate the spell template
class SpellDataWidget(tk.Frame):
    LEVEL_MAPS = ["D4Cantrip", "D6Cantrip", "D8Cantrip", "D10Cantrip", "D12Cantrip"]
    USE_COSTS = ["", "ActionPoint:1", "BonusActionPoint:1", "Movement:1", "SpellSlotsGroup:1:1:1", "WildShape:1"]

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        label = tk.Label(self, text="Spell Data")
        label.pack(side=tk.TOP)

        # Create a canvas to hold the frame with checkboxes
        left_frame = tk.Frame(self, relief="solid", borderwidth=1, takefocus=False)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)        

        # Create a canvas to hold the frame with checkboxes
        self.canvas = tk.Canvas(left_frame, height=200, relief="sunken", highlightthickness=0, takefocus=False)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create a frame inside the canvas
        canvas_frame = tk.Frame(self.canvas, takefocus=False)
        canvas_frame.place(relwidth=1)
        self.winHnd = self.canvas.create_window((0, 0), window=canvas_frame, anchor=tk.NW)

        self.fields: Dict[str, ComboWidget | EntryWidget] = {}
        props: List[str] = utils.GetValueFromKey(data.spellProperties,"All", [])
        maxWidth = 14   

        # Test generation of UI from JSON
        #for i in props:
        #    if BG3Database.GetFile(i):
        #        self.fields[i] = ComboWidget(canvas_frame, label=f"{i}:", labelWidth=maxWidth, value=BG3Database.Get(i, []))
        #        pass
        #    else:
        #        self.fields[i] = EntryWidget(canvas_frame, label=f"{i}:", labelWidth=maxWidth, value=utils.GetValueFromKey(BG3Database._defaults,i,""))
        #        pass
        #    self.fields[i].hide()


        self._ID              = EntryWidget(canvas_frame, label="Spell ID:",          labelWidth=maxWidth, value="Default_Spell_ID")
        self._Name            = EntryWidget(canvas_frame, label="Spell Name:",        labelWidth=maxWidth, value="Default Name")
        self._Description     = EntryWidget(canvas_frame, label="Spell Description:", labelWidth=maxWidth, value="Default Description")
        self._SpellType       = ComboWidget(canvas_frame, label="Spell Type:",        labelWidth=maxWidth, value=BG3Database.Get("SpellType", []))
        self._SpellAnimation  = ComboWidget(canvas_frame, label="Animation:",         labelWidth=maxWidth, value=utils.GetKeys(utils.GetValueFromKey(BG3Database.Get("SpellAnimation"), self._SpellType.data.get()), []))
        self._Trajectory      = ComboWidget(canvas_frame, label="Trajectory:",        labelWidth=maxWidth, value=utils.GetKeys(utils.GetValueFromKey(BG3Database.Get("Trajectories"), self._SpellType.data.get()), []))
        self._Level           = ComboWidget(canvas_frame, label="Level:",             labelWidth=maxWidth, value=BG3Database.Get("Level", []))
        self._SpellSchool     = ComboWidget(canvas_frame, label="School:",            labelWidth=maxWidth, value=BG3Database.Get("SpellSchool", []))
        self._TargetFloor     = ComboWidget(canvas_frame, label="Target Floor:",      labelWidth=maxWidth, value=BG3Database.Get("TargetFloor", []))
        self._Radius          = EntryWidget(canvas_frame, label="Range:",             labelWidth=maxWidth, value="18")
        self._TargetCount     = EntryWidget(canvas_frame, label="Target Count:",      labelWidth=maxWidth, value="1")
        self._ProjectileCount = EntryWidget(canvas_frame, label="Projectile Count:",  labelWidth=maxWidth, value="1")
        self._SpellRollType   = ComboWidget(canvas_frame, label="Spell Roll:",        labelWidth=maxWidth, value=data.spellRollTypes)
        self._AttackType      = ComboWidget(canvas_frame, label="Attack Type:",       labelWidth=maxWidth, value=data.attackTypes)
        self._SaveType        = ComboWidget(canvas_frame, label="Save Type:",         labelWidth=maxWidth, value=data.abilityScores)
        self._SaveDC          = ComboWidget(canvas_frame, label="Save DC:",           labelWidth=maxWidth, value=data.spellSaveDCs)
        self._PreviewCursor   = ComboWidget(canvas_frame, label="Preview Cursor:",    labelWidth=maxWidth, value=BG3Database.Get("PreviewCursor", []))
        self._DamageType      = ComboWidget(canvas_frame, label="Damage Type:",       labelWidth=maxWidth, value=BG3Database.Get("DamageType", []))
        self._VerbalIntent    = ComboWidget(canvas_frame, label="Verbal Intent:",     labelWidth=maxWidth, value=BG3Database.Get("VerbalIntent", []))

        
        #self._ID              .hide()
        #self._Name            .hide()
        #self._Description     .hide()
        #self._SpellType       .hide()
        #self._SpellAnimation  .hide()
        #self._Trajectory      .hide()
        #self._Level           .hide()
        #self._SpellSchool     .hide()
        #self._TargetFloor     .hide()
        #self._Radius          .hide()
        #self._TargetCount     .hide()
        #self._ProjectileCount .hide()
        #self._SpellRollType   .hide()
        #self._AttackType      .hide()
        #self._SaveType        .hide()
        #self._SaveDC          .hide()
        #self._PreviewCursor   .hide()
        #self._DamageType      .hide()
        #self._VerbalIntent    .hide()


        self._SpellType.data.bind("<<ComboboxSelected>>", self.on_SpellType_Changed)
        self._SpellRollType.data.bind("<<ComboboxSelected>>", self.on_SpellRoll_Changed)
        
        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Update the canvas scrolling region
        canvas_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.winHnd, width=event.width)
    
    # Filters the data in the combo box based off the 'SpellType' value
    # Disables the combo boxes if there are no valid choices
    def on_SpellType_Changed(self, event) -> None:
        spellType = self._SpellType.data.get()

        # Spell Animation
        keys = utils.GetKeys(utils.GetValueFromKey(BG3Database.Get("SpellAnimation"), spellType), [])
        self._SpellAnimation.data["values"] = keys
        self.setCombo(self._SpellAnimation, utils.GetFirstIn(keys, ""))

        # Spell Trajectory
        keys = utils.GetKeys(utils.GetValueFromKey(BG3Database.Get("Trajectories"), spellType), [])
        self._Trajectory.data["values"] = keys
        self.setCombo(self._Trajectory, utils.GetFirstIn(keys, ""))

        # Target Floor
        if spellType != "Target":
            self.setCombo(self._TargetFloor, "-1")
            self._TargetFloor.data["state"] = "disabled"
        else:
            self._TargetFloor.data["state"] = "enabled"

    # Create a function to handle the ComboBox selection event
    def on_SpellRoll_Changed(self, event) -> None:
        spellRollType = self._SpellRollType.data.get()

        if(spellRollType == "Attack"):
            self._AttackType.data["state"] = "enabled"
            self._SaveType.data["state"] = "disabled"
            self._SaveDC.data["state"] = "disabled"
        else:
            self._AttackType.data["state"] = "disabled"
            self._SaveType.data["state"] = "enabled"
            self._SaveDC.data["state"] = "enabled"

    def setEntry(self, widget: EntryWidget, value: str) -> None:
        widget.data.delete(0, tk.END)
        widget.data.insert(0, value)

    def setCombo(self, widget: ComboWidget, value: str) -> None:
        widget.data.set(value)

    def fromSpell(self, spell: models.Spell) -> None:
        self.setEntry(self._ID,              spell.id or                "Default_Spell_ID")
        self.setEntry(self._Name,            spell.getName() or         BG3Database.GetDefault("DisplayName", ""))
        self.setEntry(self._Description,     spell.description.value or BG3Database.GetDefault("Destription", ""))
        self.setEntry(self._Radius,          spell.targetRadius or      BG3Database.GetDefault("TargetRadius", ""))
        self.setEntry(self._TargetCount,     spell.targetCount or       BG3Database.GetDefault("AmountOfTargets", ""))
        self.setEntry(self._ProjectileCount, spell.projectileCount or   BG3Database.GetDefault("ProjectileCount", ""))

        self.setCombo(self._SaveDC,         spell.saveDC or         utils.GetFirstIn(data.spellSaveDCs, ""))
        self.setCombo(self._SpellRollType,  spell.rollType or       utils.GetFirstIn(data.spellRollTypes, ""))
        self.setCombo(self._AttackType,     spell.attackType or     utils.GetFirstIn(data.attackTypes, ""))
        self.setCombo(self._SaveType,       spell.saveType or       utils.GetFirstIn(data.abilityScores, ""))
        self.setCombo(self._PreviewCursor,  spell.previewCursor or  utils.GetFirstIn(BG3Database.Get("PreviewCursor"), ""))
        self.setCombo(self._TargetFloor,    spell.targetFloor or    utils.GetFirstIn(BG3Database.Get("TargetFloor"), ""))
        self.setCombo(self._VerbalIntent,   spell.verbalIntent or   utils.GetFirstIn(BG3Database.Get("VerbalIntent"), ""))
        self.setCombo(self._SpellType,      spell.spellType or      utils.GetFirstIn(BG3Database.Get("SpellType"), ""))
        self.setCombo(self._Level,          spell.level or          utils.GetFirstIn(BG3Database.Get("Level"), ""))
        self.setCombo(self._SpellSchool,    spell.school or         utils.GetFirstIn(BG3Database.Get("SpellSchool"), ""))
        self.setCombo(self._DamageType,     spell.damageType or     utils.GetFirstIn(BG3Database.Get("DamageType"), ""))

        spellType: str = self._SpellType.data.get()
        self.setCombo(self._SpellAnimation, spell.spellAnimation or utils.GetFirstIn(utils.GetValueFromKey(BG3Database.Get("SpellAnimation"), spellType), ""))
        self.setCombo(self._Trajectory,     spell.trajectory or     utils.GetFirstIn(utils.GetValueFromKey(BG3Database.Get("Trajectories"), spellType), ""))

    # Writes all the data in this widget to a spell
    def toSpell(self, spell: models.Spell) -> models.Spell:

        # Test generation of save data form auto-generated entry fields
        #save = {}
        #for (k,v) in self.fields.items():
        #    save[k] = v.data.get() or ""
        #print(save)

        spell.id = self._ID.data.get()
        spell.setName(self._Name.data.get())
        spell.setDescription(self._Description.data.get())
        spell.level = self._Level.data.get()
        spell.targetCount = self._TargetCount.data.get()
        spell.projectileCount = self._ProjectileCount.data.get()
        spell.spellType = self._SpellType.data.get()
        spell.spellAnimation = self._SpellAnimation.data.get()
        spell.trajectory = self._Trajectory.data.get()
        spell.school = self._SpellSchool.data.get()
        spell.targetRadius = self._Radius.data.get()
        spell.targetFloor = self._TargetFloor.data.get()
        spell.previewCursor = self._PreviewCursor.data.get()
        spell.damageType = self._DamageType.data.get()
        spell.rollType = self._SpellRollType.data.get()
        spell.attackType = self._AttackType.data.get()
        spell.saveType = self._SaveType.data.get()
        spell.saveDC = self._SaveDC.data.get()
        spell.verbalIntent = self._VerbalIntent.data.get()

        return spell

# A widget that holds all UI relevant to a spell
class SpellWidget(tk.Frame):
    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.ref_spell: models.Spell = None

        spellData_frame = tk.Frame(self)
        spellData_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.spellDataWidget: SpellDataWidget = SpellDataWidget(spellData_frame)
        self.spellDataWidget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                   
        icon_container = tk.Frame(spellData_frame)
        icon_container.pack(side=tk.BOTTOM, fill=tk.X, pady=2)

        self._ControllerImage = IconWidget(icon_container, label="Controller (64)")
        self._TooltipImage    = IconWidget(icon_container, label="Tooltip (380)")

        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(8,0))

        self.spellListWidget = SpellListWidget(right_frame)
        self.spellListWidget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    @property
    def ControllerImage(self) -> str:
        return self._ControllerImage.data.path

    @property
    def TooltipImage(self) -> str:
        return self._TooltipImage.data.path

    @property
    def SpellLists(self) -> List[str]:
        return self.spellListWidget.SpellLists

    def fromSpell(self, spell: models.Spell) -> None:

        self.spellDataWidget.fromSpell(spell)

        self._ControllerImage.data.display_image(spell.controllerIcon)
        self._TooltipImage.data.display_image(spell.tooltipIcon)

        # Check / Uncheck boxes to match the input spell list
        for (uuid, var) in self.spellListWidget._SpellLists:
            var.set(uuid in spell.lists)
        
        self.ref_spell = spell

    def save(self) -> None:

        save = {}
        for (k,v) in self.spellDataWidget.fields.items():
            save[k] = v.data.get() or ""

        print(save)


        self.spellDataWidget.toSpell(self.ref_spell)

        self.ref_spell.lists = self.spellListWidget.SpellLists[:]

        self.ref_spell.controllerIcon = self.ControllerImage
        self.ref_spell.tooltipIcon = self.TooltipImage

        self.ref_spell.calcMetaValues()

# A Reorderable list for spell selection and export order
# TODO: Fix bug in which you must click in the area adjacent to the label and not the label
class ReorderableList(tk.Canvas):
    hOffset = 26

    def __init__(self, master, **kwargs):
        self.cellHeight: int = kwargs.pop("cellHeight")
        self.borderPad: int = 4
        super().__init__(master, **kwargs, background="pink", relief="ridge", borderwidth=self.borderPad/2)

        self.widget_data: List[Dict[str,any]] = []
        self.drag_data = {"handle": None, "index": None}

        self.bind("<ButtonPress-1>", self.on_widget_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drag_end)
            
    def add_widget(self, widget: any, ref_uuid: str, callback: Callable[[],None]) -> None:
        i = len(self.widget_data)
        winHnd = self.create_window(self.borderPad+ReorderableList.hOffset, (i*self.cellHeight)+self.borderPad, anchor=tk.NW, window=widget)
        self.widget_data.append({"handle": winHnd, "widget": widget, "ref_uuid": ref_uuid, "callback": callback})

    def remove_widget(self, uuid: str) -> None:
        for d in self.widget_data:
            if d["ref_uuid"] == uuid:
                self.delete(d["handle"])
                self.widget_data.remove(d)
                self.redraw()
                break
    
    def redraw(self) -> None:
        for i, data in enumerate(self.widget_data):
            self.coords(data["handle"], self.borderPad+ReorderableList.hOffset, (i*self.cellHeight)+self.borderPad)

    def renameLables(self, value: Dict[str,str]) -> None:
        for d in self.widget_data:
            d["widget"].config(text=value[d["ref_uuid"]])

    def on_widget_click(self, event) -> None:
        winHnd = self.find_closest(event.x, event.y)[0]
        index = self.find_widget_index(winHnd)

        if index is not None:
            self.drag_data["handle"] = winHnd
            self.drag_data["index"] = index
            data = self.widget_data[index]
            data["callback"]()
    
    def on_drag(self, event) -> None:
        if self.drag_data["handle"] is not None:
            self.coords(self.drag_data["handle"], event.x, event.y)
    
    def on_drag_end(self, event) -> None:
        if self.drag_data["handle"] is not None:
            new_index = int(self.coords(self.drag_data["handle"])[1] / self.cellHeight)
            old_index = self.drag_data["index"]
            
            # Reorder the widgets list
            self.widget_data.insert(new_index, self.widget_data.pop(old_index))
            self.redraw()
            
            self.drag_data["handle"] = None
            self.drag_data["index"] = None
    
    def find_widget_index(self, winHnd) -> int | None:
        for (i, data) in enumerate(self.widget_data):
            if winHnd == data["handle"]:
                return i
        return None
    