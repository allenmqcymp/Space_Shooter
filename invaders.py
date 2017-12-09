import pygame as pg
import constants as c

## Setup will load graphics ##

## Top level code for setup will only be run ONCE when setup is imported ##
import setup as s

import sprites

import invaders_info as info


class Scene:

    ''' Base class for a scene
    In each loop, every scene has these 3 methods run, and init run once at setup time
    '''

    def __init__(self, persist):

        # information that if passed from a previous scene
        # it must be in the form of a dictionary
        # key - a name representing the persist variable
        # value - representing the value of the variable
        self.game_info = persist
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError


class Game(Scene):

    # Initialize everything

    def __init__(self, persist):

        Scene.__init__(self, persist)

        self.game_info = persist

        # Note: pg.init and caption setting done in setup
        self.game_over = False

        self.spaceship_projectiles = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.spaceship_sprites = pg.sprite.GroupSingle()

        # SCORE VARIABLE
        self.SCORE = 0

        # HIGH SCORE VARIABLE
        self.HIGH_SCORE = self.game_info['highscore']

        # SCORE OBJECT
        self.score_object = info.Score(c.SCORE_FONT_SIZE, c.SCORE_LOCATIONX, c.SCORE_LOCATIONY)


        # HIGH SCORE OBJECT
        self.high_score_object = info.HighScore(c.SCORE_FONT_SIZE, c.HIGHSCORE_LOCATIONX, c.HIGHSCORE_LOCATIONY)


        # control firing rate
        # bad code design
        # putting specific code to the spaceship in global scope
        # oh well
        self.firing_rate = 360
        self.last_update = pg.time.get_ticks()


        # death period - basically wait for the explosion
        self.death_period = 400
        self.death_update_tick = 0

        # generic sprite container for holding things that don't do anything special
        self.generic_container = pg.sprite.Group()

        self.setup_background()
        self.setup_spaceship()
        self.setup_enemies()

    ## Initial setup code

    def setup_background(self):
        self.background = s.GFX['space_background']

    def setup_enemies(self):
        self.enemies = sprites.EnemyGroup(self.SCORE, self.spaceship)

    def setup_spaceship(self):
        self.spaceship = sprites.Spaceship()
        self.spaceship_sprites.add(self.spaceship)

    ## Rendering code

    def render(self, surface):
        surface.blit(self.background, c.ORIGIN)
        self.spaceship_sprites.draw(surface)
        self.spaceship_projectiles.draw(surface)
        self.enemies.group.draw(surface)
        self.enemies.fireballs.draw(surface)
        self.generic_container.draw(surface)
        self.score_object.draw(surface)
        self.high_score_object.draw(surface)

    ## Event handling code

    def handle_events(self, events):

        # event handling code
        # not the best design - putting event handling in the main loop
        # but it works for this small game
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    self.spaceship.left_key_detected = True
                elif event.key == pg.K_RIGHT:
                    self.spaceship.right_key_detected = True
                elif event.key == pg.K_SPACE:
                    # Shoot! - limit shooting rate
                    now = pg.time.get_ticks()
                    if now - self.last_update > self.firing_rate:
                        self.last_update = now
                        self.spaceship.shoot = True
            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    self.spaceship.left_key_detected = False
                elif event.key == pg.K_RIGHT:
                    self.spaceship.right_key_detected = False


    ## Updating stuff code

    def update(self):


        if self.game_over:
            now = pg.time.get_ticks()
            if now - self.death_update_tick > self.death_period:
                persist = {
                    'highscore': self.HIGH_SCORE,
                    'score': self.SCORE,
                }
                self.manager.go_to(EndScreen(persist))

        # unfortunately, we need to handle the shoot in the 'global' main loop :(
        if self.spaceship.shoot:
            projectile = sprites.Sp_Projectile()
            projectile.spawn(self.spaceship.rect.x + c.SPACESHIP_WIDTH // 3,
                             self.spaceship.rect.y - c.SPACESHIP_HEIGHT // 5)
            self.spaceship_projectiles.add(projectile)
            # reset the shoot flag
            self.spaceship.shoot = False

        # we also need to check if the projectiles from the spaceship
        # has hit any of the enemies
        for projectile in self.spaceship_projectiles:
            enemy_test = pg.sprite.spritecollideany(projectile, self.enemies.group)
            if enemy_test:
                # kill the projectile and the spaceship
                self.enemies.group.remove(enemy_test)

                # add the SCORE
                self.SCORE += c.KILL_SCORE

                # create an explosion
                expl = sprites.Explosion()
                expl.set_position(enemy_test.rect.x, enemy_test.rect.y)
                self.generic_container.add(expl)

                self.spaceship_projectiles.remove(projectile)

        # for the player's side
        # check if any fireball has hit the spaceship
        # or if any enemies have hit the spaceship

        # # if so, then display an explosion, and do gameover
        for fireball in self.enemies.fireballs:
            fireball_collide = pg.sprite.spritecollideany(fireball, self.spaceship_sprites)
            if fireball_collide:
                # kill the fireball
                self.enemies.fireballs.remove(fireball_collide)

                # explode the spaceship
                expl = sprites.Explosion()
                expl.set_position(self.spaceship.rect.x, self.spaceship.rect.y)
                self.generic_container.add(expl)

                # remove the spaceship
                self.spaceship_sprites.remove(self.spaceship)

                # lose because fireball hit spaceship
                self.game_over = True

                # get the time right now
                self.death_update_tick = pg.time.get_ticks()

        # if the enemy collides with the spaceship, then display an explosion and do gameover
        enemy_collide = pg.sprite.spritecollideany(self.spaceship, self.enemies.group)
        if enemy_collide:
            expl = sprites.Explosion()
            expl.set_position(self.spaceship.rect.x, self.spaceship.rect.y)
            self.generic_container.add(expl)

            # remove the spaceship
            self.spaceship_sprites.remove(self.spaceship)

            self.game_over = True

            # get the time right now
            self.death_update_tick = pg.time.get_ticks()

        # if there are no more enemies present on the screen then we need to create some!
        if len(self.enemies.group) == 0:
            self.enemies = sprites.EnemyGroup(self.SCORE, self.spaceship)

        # update the high score after all the logic processing
        if self.SCORE > self.HIGH_SCORE:
            self.HIGH_SCORE = self.SCORE

        # update states of everything
        self.spaceship_sprites.update()
        self.spaceship_projectiles.update()
        self.enemies.update_group()
        self.generic_container.update()
        self.score_object.update(self.SCORE)
        self.high_score_object.update(self.HIGH_SCORE)




class SceneManager:
    def __init__(self):
        # this is only run ONCE
        # when scene manager is created
        # henceforth, scene manager is referred to in individual classes by a reference to self
        # very nice trick: self.scene.manager = self (this is like a singleton)
        # you only ever refer to this one scene manager instance
        persist = {
            'highscore': 0,
            'score': 0,
        }
        self.go_to(StartScreen(persist))
        self.running = True

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self

    def quit(self):
        self.running = False

# Endscreen class

class EndScreen(Scene):

    def __init__(self, persist):
        Scene.__init__(self, persist)

        self.game_info = persist

        self.background = s.GFX['space_background']

        self.txt_font_type = s.FONTS['arcade']
        self.txt_font_object = pg.font.Font(self.txt_font_type, 50)
        self.info_font_object = pg.font.Font(self.txt_font_type, 20)
        self.txt_font_surface = self.txt_font_object.render("YOU   LOST", True, c.WHITE)

        self.score_surface = self.info_font_object.render("Score  {}".format(self.game_info['score']), True, c.WHITE)
        self.highscore_surface = self.info_font_object.render("High  Score  {}".format(self.game_info['highscore']), True, c.WHITE)
        self.txt_select_surface = self.info_font_object.render("m  to  return  to  start  q  to  quit  spacebar  to  replay", True, c.WHITE)

    def update(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.manager.go_to(Game(self.game_info))
                elif event.key == pg.K_q:
                    self.manager.quit()
                elif event.key == pg.K_m:
                    self.manager.go_to(StartScreen(self.game_info))


    def render(self, screen):
        screen.blit(self.background, c.ORIGIN)
        screen.blit(self.txt_font_surface, (200, 300))
        screen.blit(self.txt_select_surface, (55, 500))
        screen.blit(self.score_surface, (235, 375))
        screen.blit(self.highscore_surface, (235, 430))


# Startscreen class

class StartScreen(Scene):

    def __init__(self, persist):
        Scene.__init__(self, persist)

        self.game_info = persist

        self.tfont_type = s.FONTS['death_star']
        self.tfont_object = pg.font.Font(self.tfont_type, 60)
        self.tfont_surface = self.tfont_object.render("SPACE SHOOTER", True, c.WHITE)

        self.txt_font_type = s.FONTS['arcade']
        self.txt_font_object = pg.font.Font(self.txt_font_type, 15)
        self.txt_start_object = pg.font.Font(self.txt_font_type, 30)

        self.prog_text_surface = self.txt_start_object.render(" PRESS  SPACEBAR  TO  START", True, c.WHITE)

        self.text1 = "It  is  the  year   2020  Enemy  Martians  have  descended  upon  the  Earth"
        self.text2 = "You  are  responsible  for  defeating  these   extraterrestrials"
        self.text4 = "Press  SPACEBAR  to  fire  an  asteroid  attack  and  destroy  their  enemy  ships"
        self.text5 = "The  future  of  the E arth  rests  in  your  hands"

        self.authortext = "Allen  Ma   Dec 2017  "

        self.text1s = self.txt_font_object.render(self.text1, False, c.WHITE)
        self.text2s = self.txt_font_object.render(self.text2, False, c.WHITE)
        self.text4s = self.txt_font_object.render(self.text4, False, c.WHITE)
        self.text5s = self.txt_font_object.render(self.text5, False, c.WHITE)

        self.texts = [self.text1s, self.text2s, self.text4s, self.text5s]

        self.authortext_surface = self.txt_font_object.render(self.authortext, True, c.WHITE)

        self.background = s.GFX['space_background']

    def handle_events(self, events):
        for event in events:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.manager.go_to(Game(self.game_info))

    def render(self, screen):
        screen.blit(self.background, c.ORIGIN)
        screen.blit(self.tfont_surface, (65, 230))
        screen.blit(self.prog_text_surface, (120, 500))
        screen.blit(self.authortext_surface, (460, 660))

        for i, text in enumerate(self.texts):
            screen.blit(text, (70, 320 + i * 30))


    def update(self):
        pass


## entry function of the program
def main():

    screen = s.SCREEN
    clock = pg.time.Clock()
    manager = SceneManager()

    while manager.running:

        if pg.event.get(pg.QUIT):
            running = False
            return

        clock.tick(c.FPS)

        manager.scene.handle_events(pg.event.get())
        manager.scene.update()
        manager.scene.render(screen)
        pg.display.update()

    pg.quit()


if __name__ == "__main__":
    main()