import json

# A static database of all the imported DATA json files
class BG3Database:
    _datafiles = {}
    _data = {}
    _defaults = {}

    @staticmethod
    def LoadData():
        with open("data/_database.json", "r") as json_file:
            BG3Database._datafiles = json.load(json_file)

        with open("data/_SpellPropertyDefaults.json", "r") as json_file:
            BG3Database._defaults = json.load(json_file)

        for k, v in BG3Database._datafiles.items():
            if v:
              with open(f"data/{v}.json", "r") as json_file:
                  BG3Database._data[k] = json.load(json_file)
    
    @staticmethod
    def Get(value, default=None):
        if value in BG3Database._data:
            return BG3Database._data[value]
        return default
    
    @staticmethod
    def GetDefault(value, default=None):
        if value in BG3Database._defaults:
            return BG3Database._defaults[value]
        return default
    
    @staticmethod
    def GetFile(value, default=None):
        if value in BG3Database._datafiles:
            return BG3Database._datafiles[value]
        return default
    
    @staticmethod
    def items():
        return BG3Database._data.items()
    

# Additional JSON files not yet in, or not relevant to being added to the database
with open("data/AbilityScores.json", "r") as json_file:
    abilityScores = json.load(json_file)

with open("data/AttackTypes.json", "r") as json_file:
    attackTypes = json.load(json_file)

with open("data/SpellLists.json", "r") as json_file:
    spellLists = json.load(json_file)

with open("data/SpellProperties.json", "r") as json_file:
    spellProperties = json.load(json_file)

with open("data/SpellRollTypes.json", "r") as json_file:
    spellRollTypes = json.load(json_file)

with open("data/SpellSaveDCs.json", "r") as json_file:
    spellSaveDCs = json.load(json_file)

