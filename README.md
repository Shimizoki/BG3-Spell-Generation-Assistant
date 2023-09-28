# BG3-Spell-Generation-Assistant
A tool to help generate templates for adding custom spells to Balder's Gate 3

Mod Name - The name of your mod (Preferred no-spaces)
Mod Path - Where to export the files. Empty will export them relative to the EXE location

Left Panel
- Allows you to add and remove spells
- You can click and drag to re-order the list.
- BUG: You must click the pink area next to the label, and not the label itself

Right panel lets you choose what lists you want this particular spell to appear on
 - Requires Spell List Combiner in your mod order (https://www.nexusmods.com/baldursgate3/mods/2577)

Center panel lets you update the data relevant to the spell
 - Dropdowns can also be used as text-entry if you know the custom data you wish to input
 - Spell ID must not have spaces and should be unique
 - You can drop your .dds controller (64x64) and Tooltip (380x380) files in the highlighted region

After Generating the files they still need to be packed using the BG3-Modders-Multitool (https://github.com/ShinyHobo/BG3-Modders-Multitool)
