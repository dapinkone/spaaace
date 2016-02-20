# just getting started with pygame.
# several bugs/dependancy issues solved by: python 3, compiling pygame 1.9.2 from source
# and apt-get install python3-dev python-dev libsdl-image1.2-dev libsdl-mixer1.2-dev
# libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev python3-numpy
# python-numpy subversion libportmidi-dev libfreetype6-dev
#
# TODO:
# enemies
# weapons fire
# colision
# death/game over condition
# score displayed bottom left

import pygame as pygame
import sys
import os.path
# sys.path.append(os.path.dirname("__file__")) # add the program root dir to path.
# from pygame.locals import * # sloppy. We can do better.

# pygame.init mysteriously crashes on debian when pygame.quit is called.
# lets use pygame.display instead, and hope that doesn't cause issues.
pygame.display.init()

fpsClock = pygame.time.Clock()  # allow limiting FPS

# define some color constants
white_color = pygame.Color(255, 255, 255)  # standard (r, g, b)
blue_color = pygame.Color(50, 50, 255)
red_color = pygame.Color(255, 50, 50)
black_color = pygame.Color(0, 0, 0)

# initialize variables
mouse_x, mouse_y = 0, 0
cursor_x, cursor_y = 0, 0
score = 0

# set_mode(width, height) making the window
screen = pygame.display.set_mode((640, 640))
pygame.display.set_caption('hello pygame :D')


class Sprite(pygame.sprite.Sprite):

    def __init__(self, image_filename, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_filename).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

class Enemy(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self, self.image, x, y)
    image = './assets/Enemy_ship.png'

    def update(self):
        super(self).update()
        self.rect.y = self.rect.y + 1
        if self.rect.y > 600:
            self.rect.y = 20

class Player(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self, self.image, x, y)
    image = './assets/SpaceShip.png'

all_sprites_list = pygame.sprite.Group()
ship_sprite = Player(300, 500) # default player position.
all_sprites_list.add(ship_sprite)
enemy_ships_group = pygame.sprite.Group()
for x in range(4):
    print("enemy {}".format(x))
    enemy = Enemy(100*x, 0)
    enemy_ships_group.add(enemy)
    all_sprites_list.add(enemy)

# the mouse appears to lag a little bit, but cursor still gets action.
# solution? no more mouse. still lags, but less game-breaking.
pygame.mouse.set_visible(False)

main_loop = True
while main_loop:  # main loop
    for event in pygame.event.get():
        if event.type in (pygame.QUIT, pygame.K_ESCAPE):
            main_loop = False
        elif event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            ship_sprite.rect.x = x
            ship_sprite.rect.y = y

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_x, mouse_y = event.pos
            print("moused, quiting out.")
            main_loop = False
            break

    screen.fill(blue_color)  # clean screen

    # paint our stuff to the screen.
    # screen.blit(ship_sprite.image, ship_sprite.rect)
    # pygame.draw.circle(screen, white_color, (cursor_x, cursor_y), 10, 10)

    # now checking for collision detection. not perfect, but enough for now.
    for sprite in pygame.sprite.spritecollide(ship_sprite, \
                                              enemy_ships_group, True):
        print("BOOM {} {}".format(score, sprite))
        score = score + 1
    all_sprites_list.draw(screen)
    pygame.display.flip()  # reveal changes

    fpsClock.tick(60)  # we don't need more than 60 fps for this. srsly.
print("mainloop finished")
pygame.quit()
# sys.exit()
