
## Utility functions ##

import pygame as pg
import os

## Loads all graphics files
def load_all_gfx(directory,accept=(".png",".jpg",".bmp")):
    """
    Load all graphics with extensions in the accept argument.  If alpha
    transparency is found in the image the image will be converted using
    convert_alpha().  If no alpha transparency is detected image will be
    converted using convert() and colorkey will be set to colorkey.
    """
    graphics = {}
    for pic in os.listdir(directory):
        name,ext = os.path.splitext(pic)
        print(name)
        if ext.lower() in accept:
            try:
                img = pg.image.load(os.path.join(directory,pic))
            except Exception as e:
                print(e)

            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
            graphics[name]=img

    print("graphics successfully loaded")
    return graphics

def load_all_fonts(directory, accept=(".ttf", ".otf")):
        fonts = {}
        for font in os.listdir(directory):
            name, ext = os.path.splitext(font)
            if ext.lower() in accept:
                print("font {}".format(name))
                fonts[name] = os.path.join(directory, font)
        print("Successfully loaded fonts")
        return fonts