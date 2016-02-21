#!/usr/bin/env python3
"""
just getting started with pygame. writing a simple space shooter.
Dependancies notes removed -- see ./Dependancies

TODO: randomly generate enemies
TODO: variety of enemy ships
TODO: item/powerup drops. Shield, weapon upgrade, diff ship, lives?
TODO: animations/sounds upon explosion of ships and firing of weapons
TODO: extra lives, and display thereof
TODO: scrolling background to give perception of movement
TODO: some sort of level progression(inc difficulty, change background)
TODO: would keyboard-driven controls be more responsive? add them.

DONE: weapons fire/collision thereof.
DONE: ships displayed/rendered
DONE: score displayed
DONE: death/game over condition
"""

import pygame
import sys
import random

# pygame.init mysteriously crashes on debian when pygame.quit is called.
# lets use pygame.display instead, and hope that doesn't cause issues.
pygame.display.init()
pygame.font.init()  # it caused issues.

fpsClock = pygame.time.Clock()  # allow limiting FPS

# define some color constants
white_color = pygame.Color(255, 255, 255)  # standard (r, g, b)
blue_color = pygame.Color(50, 50, 255)
red_color = pygame.Color(255, 0, 0)
black_color = pygame.Color(0, 0, 0)

# initialize variables
mouse_x, mouse_y = 0, 0
score = 0

# set_mode(width, height) making the window
screen = pygame.display.set_mode((640, 640))
screen_width  = screen.get_width()
screen_height = screen.get_height()

pygame.display.set_caption('hello pygame :D')


class S_Picture(pygame.sprite.Sprite):

    def __init__(self, image_filename, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_filename).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

class Enemy(S_Picture):
    def __init__(self, x, y):
        S_Picture.__init__(self, self.image, x, y)
    image = './assets/Enemy_ship.png'

    def update(self):
        self.rect.y = self.rect.y + 1
        if self.rect.y > 600:
            self.rect.y = 20


class Player(S_Picture):
    def __init__(self, x, y):
        S_Picture.__init__(self, self.image, x, y)
    image = './assets/SpaceShip.png'


class Player_bullet(S_Picture):
    def __init__(self, x, y):
        S_Picture.__init__(self, self.image, x, y)
    image = './assets/player_bullet.png'

    def update(self):
        self.rect.y = self.rect.y - 5  # move toward enemies, away from player

class Text(pygame.sprite.Sprite):
    def __init__(self, text, size=16, color=white_color, width=40, height=40):
        pygame.sprite.Sprite.__init__(self)

        self.font = pygame.font.SysFont("Arial", size)
        self.textSurf = self.font.render(text, 1, color)


player_sprite = Player(300, 500)  # default player ship pos/sprite

all_sprites_list = pygame.sprite.Group(player_sprite)
p_bullet_sprites = pygame.sprite.Group()
# generate some enemies
enemy_group = pygame.sprite.Group()
for x in range(8):
    print("enemy {}".format(x))
    enemy = Enemy(100 * x, 0)
    enemy_group.add(enemy)
all_sprites_list.add(enemy_group)


# the mouse appears to lag a little bit, but cursor still gets action.
# solution? no more mouse. still lags, but less game-breaking.
pygame.mouse.set_visible(False)

def game_over():
    screen.fill(black_color)  # clear screen.
    game_over_text = Text("GAME OVER", 40, white_color).textSurf
    game_over_x    = screen.get_width() / 2 - game_over_text.get_width() / 2
    score_text     = Text("Score: {}".format(score), 30, white_color).textSurf
    score_x        = screen.get_width() / 2 - score_text.get_width() / 2
    screen.blit(game_over_text, (game_over_x, screen.get_height() / 3))
    screen.blit(score_text, (score_x, screen.get_height() / 2))

    pygame.display.flip()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT,
                              pygame.K_ESCAPE,
                              pygame.MOUSEBUTTONUP):
                pygame.quit()  # perhaps I should add a "play again" button?
                sys.exit()

done = False
while not done:  # main loop
    for event in pygame.event.get():
        if event.type in (pygame.QUIT, pygame.K_ESCAPE):
            done = True

        # TODO: add keyboard controls here.
        # mouse controls
        elif event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            # put center of ship on mouse, not corner of picture.
            player_sprite.rect.x = x - 33
            player_sprite.rect.y = y - 33

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_x, mouse_y = event.pos
            new_bullet = Player_bullet(mouse_x, mouse_y - 20)
            p_bullet_sprites.add(new_bullet)
            all_sprites_list.add(new_bullet)
            # TODO: add bullet sound

    # now checking for collision player vs enemy ships.
    for sprite in pygame.sprite.spritecollide(player_sprite,
                                              enemy_group, True):
        game_over()

    # collision enemy vs player bullets
    for sprite in pygame.sprite.groupcollide(enemy_group,
                                             p_bullet_sprites, True, True):
        # we got one!
        score = score + 1
        # TODO: add sound/animation?
        # TODO: spawn loot drops here at position of collision.

    # clear the screen
    screen.fill(black_color)

    # update all the things!
    all_sprites_list.update()

    # draw all the things!
    all_sprites_list.draw(screen)
    screen.blit(Text("Score: {}".format(score)).textSurf, (20, 5))
    FPS_text = Text("FPS: {:.4}".format(fpsClock.get_fps())).textSurf
    screen.blit(FPS_text, (screen_width - FPS_text.get_width() - 20, 5))
    pygame.display.flip()  # reveal changes

    # slow it down, if necessary.
    fpsClock.tick(60)  # we don't need more than 60 fps for this. srsly.
game_over()
