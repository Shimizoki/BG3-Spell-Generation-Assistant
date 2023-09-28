from typing import Dict

import uuid
from PIL import Image
import os

def Generate_UUID() -> str:
    return str(uuid.uuid4())

def Generate_Handle() -> str:
    return "h"+Generate_UUID().replace("-", "")

def Resize_Image(image: Image.Image, display_width: int, display_height: int) -> Image.Image:
    # Calculate the aspect ratio
    width, height = image.size
    aspect_ratio = width / height

    # Calculate the new dimensions to fit within the maximum display size
    new_width = min(display_width, width)
    new_height = int(new_width / aspect_ratio)

    if new_height > display_height:
        new_height = display_height
        new_width = int(new_height * aspect_ratio)

    # Resize the image
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def Get_Image_Dims(value: str | Image.Image) -> tuple[int,int] | None:
    size = None
    if type(value) == str:
        if value and os.path.exists(value):
            image = Image.open(value)
            size = image.size
    elif type(value) == Image:
        size = value.size
    
    return size

def GetValueFromKey(collection: dict | list, key, default=None):
    if key and key in collection:
        return collection[key]
    return default

def GetKeyFromValueIn(collection: dict | list, value, default=None):
    if collection and value:
        if type(collection) == dict:
            for (k,v) in collection.items():
                if v == value:
                    return k
                
        elif type(collection) == list:
            for (k,v) in collection:
                if v == value:
                    return k
    
    return default

def GetFirstIn(collection: dict | list, default=None):
    if collection and len(collection) > 0:
        if type(collection) == dict:
            return next(iter(collection.keys()))
                
        elif type(collection) == list:
            return collection[0]

    return default

def GetKeys(collection: dict | list, default=None):
    if collection:
        if type(collection) == dict:
            return list(collection.keys())
                
        elif type(collection) == list:
            return [k for (k,_) in collection]
        
    return default

def PopKwArgs(args: Dict[str,any], key: str, default = None):
    return args.pop(key) if key in args else default