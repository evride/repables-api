import PIL
from PIL import Image
from utils import saveS3File
from pathlib import Path
import time
from datetime import datetime


imageSizes = [
        { "width":1440, "height":1080, "type": "large" },
        { "width":1280, "height":960, "type": "medium" },
        { "width":640, "height":480, "type": "small" },
        { "width":320, "height":240, "type": "thumbnail" }
    ]

def resize_image(srcImage:str, destImage:str, width:int, height:int):
    with Image.open(srcImage) as img:
        im = img.resize((width, height), PIL.Image.BICUBIC)
        #im.thumbnail((width, height))
        destSplit = destImage.split(".")
        fileType = destSplit[-1].upper()
        im.save(destImage, fileType, optimize = True)
        saveS3File(destImage, destImage)
        Path(destImage).unlink()



def create_scaled_images(srcImage):
    filenameBase = str(int(time.time() * 1000))
    images = []
    for size in imageSizes:
        destImage = "images/" + filenameBase + "_" + size["type"] + ".png"
        images.append({ **size, "filename": destImage})
        print("../files/" + srcImage + " : " + destImage + " : " + str(size["width"]) + " : " + str(size["height"]))
        resize_image("../files/" + srcImage, destImage, size["width"], size["height"])
    return images

    
    