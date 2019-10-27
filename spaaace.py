#!/usr/bin/env python3
"""
just getting started with pygame. writing a simple space shooter.
Dependancies notes removed -- see ./Dependancies

TODO, features requested/required still to be done, removed to
./TODO.org
"""

import os
import pygame
import sys
import random
import time
import math

if not (sys.version.startswith("3.")):
    print("Error: Python 3 required. Python 2 is not supported.")
    quit()

# pygame.init mysteriously crashes on debian when pygame.quit is called.
# lets use pygame.display instead, and hope that doesn't cause issues.
pygame.display.init()
pygame.font.init()  # it caused issues. required for text.
pygame.mixer.init()  # for sound

# in case we're running the game from a shortcut or remotely or somethin
# lets cd to the project dir so relative filenames work
# os.chdir(os.path.dirname(__file__))

test_sound_file = "./assets/drip.ogg"
test_sound = pygame.mixer.Sound(test_sound_file)

fpsClock = pygame.time.Clock()  # allow limiting FPS

# DEFINE CONSTANTS
WHITE = pygame.Color(255, 255, 255)  # standard (r, g, b)
BLUE = pygame.Color(50, 50, 255)
RED = pygame.Color(255, 0, 0)
BLACK = pygame.Color(0, 0, 0)
GREEN = pygame.Color(0, 255, 0)

###################################
# initialize variables
##################################
mouse_x, mouse_y = 0, 0
score = 0
high_score = 0
start_time = time.time()  # tracking how long we've been in-game.

# set_mode(width, height) making the window
screen = pygame.display.set_mode((1920, 960))
pygame.display.toggle_fullscreen()
screen_width = screen.get_width()
screen_height = screen.get_height()
pygame.display.set_caption("SPAAACE bubbles!")

all_sprites_list = pygame.sprite.Group()
enemy_counter = 0

#########################################
# CLASSES
#########################################


class S_Picture(pygame.sprite.Sprite):
  #  def behavior(self, t):
  #      pass
    def die(self):
        pass

    def __init__(self, image_filename, location, hostile=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_filename).convert_alpha()
        # rotation of images causes deformation.
        # keep origin on file for reference.
        self.origin_img = self.image
        self.rect = self.image.get_rect()
        self.origin = location
        self.move(self.origin)
        self.mask = pygame.mask.from_surface(self.image)
        self.frames_alive = 0
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.hostile = hostile
        # enemies, player, bullets, etc. they all need health pools.
        self.health = 1
        self.orientation = 0 # angle offset

    def move(self, location):
        self.rect.x = location[0]
        self.rect.y = location[1]

    def update(self):
        self.frames_alive += 1
        if 'behavior' in dir(self):
            self.behavior(self.frames_alive) # movement behavior.

    def spawn_bullet(self):
        new_bullet = Bullet(
            location=(self.rect.x + self.width / 2, self.rect.y),
            hostile=self.hostile,
        )
        all_sprites_list.add(new_bullet)


class Player(S_Picture):
    def __init__(self, location):
        super().__init__(self.image_filename, location)
        self.hostile = False

    image_filename = "./assets/SpaceShip.png"
    bullet_type = 0  # default type....this seems cryptic. #TODO #FIXME


player_sprite = Player((screen_width/2, screen_height/2))


class Bullet(S_Picture):
    def default_behavior(self, t):
        #print(f"t={t}")
        x = self.origin[0]
        if not self.hostile:
            y = self.origin[1] - 8 * t  # vertical trajectory
        else:
            y = self.origin[1] + 8 * t # default for enemy bullets.(?)
        self.move((x, y))

    def __init__(
        self,
        location,
        hostile=False,
        behavior=None,
        image_filename="./assets/player_bullet.png",
    ):
        super().__init__(image_filename, location)


        if behavior is None:
            self.behavior = self.default_behavior
        else:
            self.behavior = behavior
        self.hostile = hostile
        self.image_filename = image_filename
        self.health = 1  #

    def update(self):
        super().update()
        # destroy sprite if it's out of range.
        if self.rect.y < 0 or self.rect.y > screen_height:
            all_sprites_list.remove(self)


class Enemy(S_Picture):
    image_filename = "./assets/scary_bubbles.png"

    def __init__(self, location, vector=(0, 1)):
        S_Picture.__init__(self, self.image_filename, location)
        self.v_x, self.v_y = vector
        self.relocate()  # find a good initial position.
        self.health = 1
        global enemy_counter
        enemy_counter += 1
        all_sprites_list.add(self)

    def update(self):
        super().update()
        self.rect.y = self.rect.y + self.v_y  # TODO: varied behavior?
        self.rect.x = self.rect.x + self.v_x
        if self.rect.y > screen_height:
            self.rect.y = 0
            self.relocate()
        if self.rect.x > screen_width:
            self.rect.x = 0
        if self.rect.x < 0 - self.width:
            self.rect.x = screen_width

        if self.frames_alive % 10 == 0:  # bullet every 10 frames.
            self.spawn_bullet()

    def relocate(self):
        attempts = 0
        # keep trying to find a free spot. give it a few tries.
        all_sprites_list.remove(self)  # if it already exists = inf collision
        self.move((random.randrange(0, screen_width - 60),  0))
        #while pygame.sprite.spritecollide(self, all_sprites_list, False):
        #    attempts = attempts + 1
            # prevent inf loop by repositioning in y
            # FIXME: does this actually prevent inf loop? or just
            # make a train along the y axis?
        #    if attempts > 10:
        #        self.rect.y = self.rect.y - 20
        all_sprites_list.add(self)

    def die(self):
        global enemy_counter
        enemy_counter -= 1

class Text(pygame.sprite.Sprite):
    def __init__(self, text, size=16, color=WHITE, width=40, height=40):
        # this object doesn't use width or height? FIXME?
        pygame.sprite.Sprite.__init__(self)

        self.font = pygame.font.SysFont("Arial", size)
        self.textSurf = self.font.render(text, 1, color)


##############################
# function definitions
#############################


def pixel_collision(sprite_a, sprite_b):  # pixel perfect collision
    if sprite_a.hostile == sprite_b.hostile:
        # TODO: exception/handling for upgrades here.
        # they're on the same team dont' worry about it.
        return False

    rect_a = sprite_a.rect
    rect_b = sprite_b.rect
    offset_x, offset_y = (rect_b.left - rect_a.left), (rect_b.top - rect_a.top)
    if sprite_a.mask.overlap(sprite_b.mask, (offset_x, offset_y)) is not None:
        return True
    else:
        return False


def spawn_enemies(quantity):
    for x in range(quantity):
        Enemy(location=(0, screen_height / 2), vector=(random.randint(-1, 1), 1))


def game_over():  # game over screen/menu?
    pygame.mouse.set_visible(True)
    global score
    game_over_text = Text("GAME OVER", 40, WHITE).textSurf
    game_over_x = screen_width / 2 - game_over_text.get_width() / 2
    score_text = Text("Score: {}".format(score), 30, WHITE).textSurf
    score_text_x = screen_width / 2 - score_text.get_width() / 2
    again_text = Text("Press Space", 30, GREEN).textSurf
    again_text_x = screen_width / 2 - again_text.get_width() / 2
    screen.blit(game_over_text, (game_over_x, screen_height / 3))
    screen.blit(score_text, (score_text_x, screen_height / 2))
    screen.blit(again_text, (again_text_x, screen_height / 1.5))

    pygame.display.flip()
    done = False
    while not done:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    print(event.key, " recieved!")
                    reset_game()
                elif event.key is pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    print(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass  # TODO add continue button.
        fpsClock.tick(15)


def reset_game():
    global score
    score = 0
    global start_time
    start_time = time.time()
    global enemy_counter
    enemy_counter = 0
    player_sprite.health = 1
    all_sprites_list.remove(all_sprites_list)
    screen.fill((0,0,0))
    main()


def main():
    pygame.mouse.set_visible(False)
    all_sprites_list.add(player_sprite)
    done = False
    mouse_button_pressed = False
    bullet_delay = 3  # allow a bullet fired every N frames
    bullet_timer = bullet_delay
    print("Ready.")
    while not done:  # main loop
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.K_ESCAPE):
                done = True
            # TODO: add keyboard controls here.
            # mouse controls
            elif event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                # put center of ship on mouse, not corner of picture.
                player_sprite.move(
                    (
                        x - player_sprite.width / 2,
                        y + player_sprite.height / 2,
                    )
                )

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_button_pressed = False
        if mouse_button_pressed is True:  # auto fire
            if bullet_timer == 0:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # FIXME: should be a spawn_sprite(location) method.
                player_sprite.spawn_bullet()
                bullet_timer = bullet_delay
            else:
                bullet_timer = bullet_timer - 1

        if player_sprite.health <= 0:
            game_over()

        # collision enemy vs sprite_as
        for sprite_a in all_sprites_list:
            for sprite_b in all_sprites_list:
                if pixel_collision(sprite_a, sprite_b):
                    # deal damage to both parties.
                    temp = sprite_b.health
                    sprite_b.health = sprite_b.health - sprite_a.health
                    sprite_a.health = sprite_a.health - temp
                    # parsing out the consequences.
                    for s in [sprite_a, sprite_b]:
                        if s.health <= 0:  # sprite_b death
                            all_sprites_list.remove(s)
                            global score
                            score = score + 1
                            test_sound.play()
                            # there's gotta be a better way....
                            s.die()
        # TODO: add sound/animation?
        # if enemies have been destroyed, lets spawn some new ones.
        # TODO: further complicate with level formula/speeds/balance
        timer = int(time.time() - start_time)

        ## TODO: what does this formula even do?
        # if len(all_sprites_list) < timer + 1 / (1 + sum(range(1, timer))):
        if timer % 3600 == 0 and enemy_counter < 20:
            spawn_enemies(1)
        # update all the things!
        all_sprites_list.update()

        # paint bg, clear the field.
        screen.fill((0, 0, 0))
        # TODO: need a better background.
        # draw all the things!
        all_sprites_list.draw(screen)
        screen.blit(Text("Score: {}".format(score)).textSurf, (20, 5))
        FPS_text = Text("FPS: {:.4}".format(fpsClock.get_fps())).textSurf
        screen.blit(FPS_text, (screen_width - FPS_text.get_width() - 20, 5))

        global high_score
        if high_score <= score:
            high_score = score

        High_score_text = Text(
            "High Score: {}".format(high_score)
        ).textSurf  # pep8 pls ;_;
        screen.blit(
            High_score_text, ((screen_width / 2 - High_score_text.get_width() / 2), 5)
        )
        pygame.display.flip()  # reveal changes

        # slow it down, if necessary.
        fpsClock.tick(60)  # we don't need more than 60 fps for this. srsly.

try:
    main()
except Exception as e:
    print(e)
finally:
    pygame.quit()
