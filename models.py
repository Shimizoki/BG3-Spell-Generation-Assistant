from typing import List

import xml.etree.ElementTree as ET

from utils import utils
from data import BG3Database

# The Datastructure of a localizied string
class Localization:
    def __init__(self, uuid: str, version: str, value: str) -> None:
        self.uuid: str = uuid
        self.version: str = version
        self.value: str = value

    def __str__(self) -> str:
        return str(ET.tostring(self.toXML()))
    
    def toXML(self) -> ET.Element:
        root = ET.Element("content")
        root.text = self.value
        root.set("contentuid", self.uuid)
        root.set("version", self.version)

        return root

# The Datastrucure of a spell
class Spell:    
    def __init__(self, uuid: str) -> None:
        self.uuid: str = uuid
        self.id: str = None
        self.name = Localization(uuid=utils.Generate_UUID(), version="1", value="Default Name")
        self.description = Localization(uuid=utils.Generate_UUID(), version="1", value="Default Description")

        self.spellType: str = None
        self.spellAnimation: str = None
        self.trajectory: str = None
        self.level: str = None
        self.school: str = None
        self.targetFloor: str = None
        self.targetRadius: str = None
        self.targetCount: str = None
        self.projectileCount: str = None
        self.spellRoll: str = None
        self.tooltipAttackSave: str = None
        self.rollType: str = None
        self.attackType: str = None
        self.saveType: str = None
        self.saveDC: str = None
        self.previewCursor: str = None
        self.damageType: str = None
        self.verbalIntent: str = None
        
        self.depends: List[str] = []
        self.lists: List[str] = []
        self.controllerIcon: str = None
        self.tooltipIcon: str = None
    
    def __str__(self) -> str:
        return (""
        + "" + f'new entry "{self.spellType}_{self.id}"'
        + "\n" + f'type "SpellData"'
        + "\n" + f'data "SpellType" "{self.spellType}"'
        + "\n" + f'using ""'
        + "\n" + f'data "SpellContainerID" ""'
        + "\n" + f'data "ContainerSpells" ""'
        + "\n" + f'data "Level" "{self.level}"'
        + "\n" + f'data "SpellSchool" "{self.school}"'
        + "\n" + f'data "SpellProperties" "GROUND:SurfaceChange(Ignite);GROUND:SurfaceChange(Melt)"'
        + "\n" + f'data "TargetFloor" "{self.targetFloor}"'
        + "\n" + f'data "TargetRadius" "{self.targetRadius}"'
        + "\n" + f'data "SpellRoll" "{self.spellRoll}"'
        + "\n" + f'data "SpellSuccess" "IF(not CharacterLevelGreaterThan(16)):DealDamage(LevelMapValue(D10Cantrip),{self.damageType},Magical);IF(CharacterLevelGreaterThan(16)):DealDamage(4d10,{self.damageType},Magical)"'
        + "\n" + f'data "TargetConditions" "not Self() and not Dead()"'
        + "\n" + f'data "AmountOfTargets" "{self.targetCount}"'
        + "\n" + f'data "ProjectileCount" "{self.projectileCount}"'
        + "\n" + f'data "Trajectories" "{self._NameToTrajectory()}"'
        + "\n" + f'data "Icon" "{self.id}"'
        + "\n" + f'data "DisplayName" "{self.name.uuid};1"'
        + "\n" + f'data "Description" "{self.description.uuid};1"'
        + "\n" + f'data "TooltipDamageList" "DealDamage(LevelMapValue(D10Cantrip),{self.damageType})"'
        + "\n" + f'data "TooltipAttackSave" "{self.tooltipAttackSave}"'
        + "\n" + f'data "PrepareSound" "Spell_Prepare_Damage_Fire_Gen_L1to3"'
        + "\n" + f'data "PrepareLoopSound" "Spell_Prepare_Damage_Fire_Gen_L1to3_Loop"'
        + "\n" + f'data "CastSound" "Spell_Cast_Damage_Fire_FireBolt_L1to3"'
        + "\n" + f'data "PreviewCursor" "{self.previewCursor}"'
        + "\n" + f'data "CastTextEvent" "Cast"'
        + "\n" + f'data "CycleConditions" "Enemy() and not Dead()"'
        + "\n" + f'data "UseCosts" "ActionPoint:1"'
        + "\n" + f'data "SpellAnimation" "{self._NameToAnimation()}"'
        + "\n" + f'data "VerbalIntent" "{self.verbalIntent}"'
        + "\n" + f'data "SpellFlags" "HasVerbalComponent;HasSomaticComponent;IsSpell;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold;IsHarmful"'
        + "\n" + f'data "HitAnimationType" "MagicalDamage_External"'
        + "\n" + f'data "PrepareEffect" "c88e9cfa-df92-477a-ae75-cbfb932350b4"'
        + "\n" + f'data "CastEffect" "e235ca47-1bf5-4587-9475-cf191b6005f9"'
        + "\n" + f'data "DamageType" "{self.damageType}"'
        )

    def _NameToAnimation(self) -> str:
        return self._NameToKeyedValue(name=self.spellAnimation, key=self.spellType, collection=BG3Database.Get("SpellAnimation"))
    
    def _NameToTrajectory(self) -> str:
        return self._NameToKeyedValue(name=self.trajectory, key=self.spellType, collection=BG3Database.Get("Trajectories"))
    
    def _NameToKeyedValue(self, name: str, key: str, collection: dict) -> str:
        if key and name:
            if key in collection:
                if name in collection[key]:
                    return collection[key][name]
        return name or ""

    def setName(self, value: str) -> None:
        self.name.value = value

    def getName(self) -> str:
        return self.name.value

    def setDescription(self, value: str) -> None:
        self.description.value = value

    def calcMetaValues(self) -> None:
        if self.rollType == "Attack":
            self.spellRoll = f"Attack(AttackType.{self.attackType})"
            self.tooltipAttackSave = f"{self.attackType}"
        else:
            self.spellRoll = f"not SavingThrow(Ability.{self.saveType}, {self.saveDC})"
            self.tooltipAttackSave = f"{self.saveType}"

# A Tuple of paths for moving files
class PathVector:
    def __init__(self, inPath: str, outPath: str):
        self.inPath: str = inPath
        self.outPath: str = outPath

    