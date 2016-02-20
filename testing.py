# just getting started with pygame.
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

# pygame.init crashes on debian when pygame.quit is called.
# lets use pygame.display instead. hope that doesn't cause issues.
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


# set_mode(width, height) making the window
screen = pygame.display.set_mode((640, 640))
pygame.display.set_caption('hello pygame :D')

# sprites
ship_img = './assets/SpaceShip.bmp'
enemy_ship_img = './assets/Enemy_ship.png'


class Sprite(pygame.sprite.Sprite):

    def __init__(self, image_filename, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image = pygame.image.load(image_filename).convert_alpha()
        self.rect = self.image.get_rect()

ship_sprite = Sprite(ship_img, 20, 20)
enemy_ship_sprite = Sprite(enemy_ship_img, 30, 30)

# default locations:
ship_sprite.rect.topleft = [300, 500]
enemy_ship_sprite.rect.topleft = [300, 10]

# the mouse appears to lag a little bit, but cursor still gets action.
# solution? no more mouse. still lags, but less game-breaking.
pygame.mouse.set_visible(False)

main_loop = True
while main_loop:  # main loop
    for event in pygame.event.get():
        if event.type in (pygame.QUIT, pygame.K_ESCAPE):
            main_loop = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            ship_sprite.rect.topleft = [mouse_x, mouse_y]

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_x, mouse_y = event.pos
            print("moused, quiting out.")
            main_loop = False
            break

    screen.fill(blue_color)  # clean screen

    # paint our stuff to the screen.
    screen.blit(ship_sprite.image, ship_sprite.rect)
    # pygame.draw.circle(screen, white_color, (cursor_x, cursor_y), 10, 10)
    screen.blit(enemy_ship_sprite.image, enemy_ship_sprite.rect)  # temp coordinates for testing.

    # now checking for collision detection
    #for sprite in pygame.sprite.spritecollide(ship_sprite, enemy_ship_sprite, True):
    #    print("BOOM")

    pygame.display.flip()  # reveal changes

    fpsClock.tick(60)  # we don't need more than 60 fps for this. srsly.
print("mainloop finished")
pygame.quit()
sys.exit()
