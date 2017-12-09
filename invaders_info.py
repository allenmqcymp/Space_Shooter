## Classes for scores and high score and what not that updates in game ##

import constants as c
import pygame as pg
import setup as s

class Score:

    def __init__(self, font_size, x, y):

        self.font_type = s.FONTS['zerovelo']
        self.font = pg.font.Font(self.font_type, font_size)
        self.font_surface = self.font.render("Score: 0", True, c.WHITE)
        self.x = x
        self.y = y

    def update(self, score):
        '''
        :param score: integer score
        :return: Nothing
        updates self.font to the
        '''
        self.font_surface = self.font.render("Score: " + str(score), True, c.WHITE)

    def draw(self, surface):
        surface.blit(self.font_surface, (self.x, self.y))


class HighScore(Score):

    def __init__(self, font_size, x, y):
        Score.__init__(self, font_size, x, y)

    def update(self, score):
        self.font_surface = self.font.render("High Score: " + str(score), True, c.WHITE)