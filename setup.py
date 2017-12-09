import pygame as pg
import os
import constants as c
from tools import *


## Top level Code ##

os.environ['SDL_VIDEO_CENTERED'] = '1'
SCREEN = pg.display.set_mode(c.SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()

pg.init()
pg.display.set_caption(c.CAPTION)

GFX = load_all_gfx(os.path.join("resources", "graphics"))
FONTS = load_all_fonts(os.path.join("resources", "fonts"))

