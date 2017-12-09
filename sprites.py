import pygame as pg
import setup as s
import constants as c

import random

class Spaceship(pg.sprite.Sprite):

    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.image = s.GFX['ufo']
        self.rect = self.image.get_rect()
        self.rect.x = c.INIT_SPACESHIP_X
        self.rect.y = c.INIT_SPACESHIP_Y

        self.left_key_detected = False
        self.right_key_detected = False
        self.shoot = False


    def update(self):

        if self.left_key_detected:
            self.rect.x -= c.MOVE_INCREMENT

            # detect out of bounds
            if self.rect.x < 0:
                self.rect.x = 0

        if self.right_key_detected:
            self.rect.x += c.MOVE_INCREMENT

            # detect out of bounds
            if self.rect.x > c.SCREEN_WIDTH - c.SPACESHIP_WIDTH:
                self.rect.x = c.SCREEN_WIDTH - c.SPACESHIP_WIDTH


class Enemy(pg.sprite.Sprite):

    def __init__(self, score):
        pg.sprite.Sprite.__init__(self)

        self.image = s.GFX['enemy']
        self.rect = self.image.get_rect()

        self.alive = True
        self.rect.x = c.INIT_ENEMY_X
        self.rect.y = c.INIT_ENEMY_Y

        if score >= 800:
            self.x_move_increment = c.MOV_X_600
            self.y_move_increment = c.MOV_Y_600
        elif score >= 600:
            self.x_move_increment = c.MOV_X_600
            self.y_move_increment = c.MOV_Y_600
        elif score >= 400:
            self.x_move_increment = c.MOV_X_400
            self.y_move_increment = c.MOV_Y_400
        elif score >= 200:
            self.x_move_increment = c.MOV_X_200
            self.y_move_increment = c.MOV_Y_200
        else:
            self.x_move_increment = c.INIT_MOV_X
            self.y_move_increment = c.INIT_MOV_Y


        self.shoot_fireball = False

        # the higher the value, the more frequently the
        # spaceships will shoot fireballs
        self.fireball_counter = 0
        self.fireball_count_threshold = random.randint(80, 120)

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y



    def update(self):

        self.rect.x += self.x_move_increment

class Explosion(pg.sprite.Sprite):

    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.explosion_graphics = []

        # get explosion images
        self.num_images = 8
        for i in range(self.num_images):
            name = "explosion{}".format(i)
            self.explosion_graphics.append(s.GFX[name])

        # position of the rectangle
        self.collision_x = None
        self.collision_y = None

        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = c.FPS

        self.image = self.explosion_graphics[self.frame]
        self.rect = self.image.get_rect()

    def set_position(self, x, y):
        if not self.collision_x:
            self.collision_x = x
        if not self.collision_y:
            self.collision_y = y

        self.rect.x = x
        self.rect.y = y


    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            # increase the sprite counter each frame
            if self.frame == self.num_images - 1:
                self.kill()
            else:
                self.image = self.explosion_graphics[self.frame]


class EnemyGroup():

    def __init__(self, score, spaceship):
        self.too_close = False

        self.spaceship = spaceship
        self.score = score

        self.num_enemies = 4
        self.group = pg.sprite.Group()

        self.fireballs = pg.sprite.Group()

        self.enemy_left = Enemy(score)
        self.enemy_left.set_position(c.INIT_ENEMY_X, c.INIT_ENEMY_Y)
        self.group.add(self.enemy_left)

        self.enemy_center = Enemy(score)
        self.enemy_center.set_position(2 * c.INIT_ENEMY_X, c.INIT_ENEMY_Y)
        self.group.add(self.enemy_center)

        self.enemy_right = Enemy(score)
        self.enemy_right.set_position(3 * c.INIT_ENEMY_X, c.INIT_ENEMY_Y)
        self.group.add(self.enemy_right)

        self.enemy_down = Enemy(score)
        self.enemy_down.set_position(2 * c.INIT_ENEMY_X, c.INIT_ENEMY_Y + c.ENEMY_HEIGHT+ c.ENEMY_VERT_DIST)
        self.group.add(self.enemy_down)

    def update_group(self):

        # updating logic for the enemy
        for enemy in self.group:
            enemy.update()

            enemy.fireball_counter += 1

            # if counter reaches update count, shoot a fireball
            if enemy.fireball_counter == enemy.fireball_count_threshold:
                enemy.shoot_fireball = True
                # reset the counter
                enemy.fireball_counter = 0

            # fireball handling code
            if enemy.shoot_fireball:
                # set fireball shoot to false
                enemy.shoot_fireball = False

                # really bad coding style - adding hardcoded score in a random update place
                # but basically set homing to true when score is greater than 300
                if self.score >= 300:
                    fireball = Fireball(self.spaceship, homing=True)
                    fireball.update_pos(enemy.rect.centerx, enemy.rect.centery)
                    self.fireballs.add(fireball)
                else:
                    fireball = Fireball()
                    fireball.update_pos(enemy.rect.centerx, enemy.rect.centery)
                    self.fireballs.add(fireball)



            if (enemy.rect.x < 0) or \
                (enemy.rect.x > c.SCREEN_WIDTH - c.ENEMY_WIDTH):
                self.too_close = True
                break

        # updating logic for the fireball
        for fireball in self.fireballs:
            fireball.update()

        if self.too_close:
            for enemy in self.group:
                enemy.x_move_increment *= -1
                # if the enemies reach the bottom line,
                # then just shuffle horizontally
                if not (enemy.rect.y >= c.INIT_SPACESHIP_Y - 40 ):
                    enemy.rect.y += enemy.y_move_increment
                self.too_close = False
                enemy.update()

class Fireball(pg.sprite.Sprite):
    """
    a projectile shot by the enemy
    homing missile - tracks the spaceship movement
    moves itself according to current spaceship movement relative to itself
    behaves with artificial gravity
    # note that if you choose homing you must also fill out spaceship refernece to the fireball
    # otherwise, it will have no refernece to the spaceship
    """

    def __init__(self, spaceship=None, homing=False):

        pg.sprite.Sprite.__init__(self)

        self.image = s.GFX['fireball']
        self.rect = self.image.get_rect()

        self.xmove_increment = c.FIREBALL_XMOVE_INCREMENT
        self.ymove_increment = c.FIREBALL_YMOVE_INCREMENT
        self.acceleration = c.GRAVITY

        self.homing = homing
        if self.homing:
            self.spaceship = spaceship
            self.spaceshipx = self.spaceship.rect.centerx


    def update_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.ymove_increment += self.acceleration
        if self.ymove_increment >= c.FIREBALL_MAX_YSPEED:
            self.ymove_increment = c.FIREBALL_MAX_YSPEED
        self.rect.y += self.ymove_increment

        if self.homing:
            # update the coordinates of the spaceship
            self.spaceshipx = self.spaceship.rect.x

            if self.rect.x < self.spaceshipx:
                self.rect.x += self.xmove_increment
            elif self.rect.x > self.spaceshipx:
                self.rect.x -= self.xmove_increment


        # kill the sprite if it moves out of screen
        if self.rect.y <= 0:
            self.kill()


# Spaceship's projectile
class Sp_Projectile(pg.sprite.Sprite):

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = s.GFX['asteroid']
        self.acceleration = c.SP_PROJECTILE_ACCELERATION
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.move_increment = c.SP_PROJECTILE_MOVE_INCREMENT

    def spawn(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.move_increment += self.acceleration
        if self.move_increment >= c.SP_PROJECTILE_MAX_SPEED:
            self.move_increment = c.SP_PROJECTILE_MAX_SPEED
        # asteroid moves upwards
        self.rect.y -= self.move_increment

        # kill the sprite if it moves out of screen
        if self.rect.y <= 0:
            self.kill()