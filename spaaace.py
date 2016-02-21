#!/usr/bin/env python3
"""
just getting started with pygame. writing a simple space shooter.
Dependancies notes removed -- see ./Dependancies

TODO: variety of enemy ships(diff ships=diff speeds/drops?)
TODO: item/powerup drops: Shield, weapon upgrade, diff ship, lives?
TODO: add item drop: change of player ship(req weapon reset?)
TODO: animations upon collisions, firing of weapons
TODO: sounds - weapon, ship-ship collision, weapon-ship collision
TODO: extra lives, and display thereof
TODO: some sort of level progression(inc difficulty, change background)
TODO: would keyboard-driven controls be more responsive? add them.
TODO: perhaps make enemy moving more diverse than straight lines?
TODO: implement enemy health pools?
TODO: boundaries to player ship: prevent moving off-screen to safety
TODO: PAUSE feature
TODO: game_over() continue button.

DONE: proper enemy size-specific placement # accidentally via collision.
DONE: make collision system pixel perfect.
DONE: randomly generate enemies
DONE: rather than clearing screen on game_over, freezeframe?
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
pygame.font.init()   # it caused issues. required for text.
pygame.mixer.init()  # for sound

test_sound_file = './assets/drip.ogg'
test_sound = pygame.mixer.Sound(test_sound_file)


fpsClock = pygame.time.Clock()  # allow limiting FPS

# DEFINE CONSTANTS
white = pygame.Color(255, 255, 255)  # standard (r, g, b)
blue  = pygame.Color(50, 50, 255)
red   = pygame.Color(255, 0, 0)
black = pygame.Color(0, 0, 0)
green = pygame.Color(0, 255, 0)

#########################################
# CLASSES
#########################################
class S_Picture(pygame.sprite.Sprite):

    def __init__(self, image_filename, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_filename).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

class Player(S_Picture):
    def __init__(self, x, y):
        S_Picture.__init__(self, self.image_filename, x, y)
    image_filename = './assets/SpaceShip.png'

class Player_bullet(S_Picture):
    # x, y for current location.
    # v_x, v_y for vector/speed/movement calculations.
    def __init__(self, x, y, vector = (0, -5)):
        S_Picture.__init__(self, self.image_filename, x, y)
        self.v_x, self.v_y = vector
    image_filename = './assets/player_bullet.png'

    def update(self):
        self.rect.y = self.rect.y + self.v_y
        self.rect.x = self.rect.x + self.v_x
        if self.rect.y < 0:  # destroy sprite if it's out of range.
            p_bullet_sprites.remove(self)
            all_sprites_list.remove(self)

class Enemy(S_Picture):
    def __init__(self, x = 0, y = 0, vector = (0, 1)):
        S_Picture.__init__(self, self.image_filename, x, y)
        self.v_x, self.v_y = vector
        self.relocate()  # find a good initial position.
        enemy_group.add(self)
        all_sprites_list.add(self)
    image_filename = './assets/scary_bubbles.png'

    def update(self):
        self.rect.y = self.rect.y + self.v_y
        self.rect.x = self.rect.x + self.v_x
        if self.rect.y > screen_height:
            self.rect.y = 0
            self.relocate()
        if self.rect.x > screen_width:
            self.rect.x = 0
        if self.rect.x < 0:
            self.rect.x = screen_width

    def relocate(self):
            attempts = 0
            # keep trying to find a free spot. give it a few tries.
            enemy_group.remove(self)  # if it already exists = inf collision
            self.rect.x = get_rand_x()
            self.rect.y = 0
            while(pygame.sprite.spritecollide(self, enemy_group, False)):
                attempts = attempts + 1
                if attempts > 10:  # prevent infinite looping here.
                    self.rect.y = self.rect.y - 20
                    # print("too many tries, moving up in y")
            enemy_group.add(self)

class Bg_Picture(S_Picture):
    def __init__(self, image_filename):
        self.image_filename = image_filename
        S_Picture.__init__(self, self.image_filename, 0, -1782 + screen_height)

class Text(pygame.sprite.Sprite):
    def __init__(self, text, size=16, color=white, width=40, height=40):
        pygame.sprite.Sprite.__init__(self)

        self.font = pygame.font.SysFont("Arial", size)
        self.textSurf = self.font.render(text, 1, color)
###################################
# initialize variables
##################################
mouse_x, mouse_y = 0, 0
score = 0
timer = 0  # tracking how long we've been in-game.

# set_mode(width, height) making the window
screen = pygame.display.set_mode((640, 640))
screen_width  = screen.get_width()
screen_height = screen.get_height()
pygame.display.set_caption('SPAAACE bubbles!')

all_sprites_list = pygame.sprite.Group()
p_bullet_sprites = pygame.sprite.Group()
enemy_group      = pygame.sprite.Group()

lvl_one_bg = Bg_Picture('./assets/level one.png')

def get_rand_x():  # randomized location for new ships.
    # TODO: this may be more efficient taking into account width of the ship
    return(random.randrange(0, screen_width - 60))

def pixel_collision(sprite_a, sprite_b):  # pixel perfect collision
    rect_a = sprite_a.rect
    rect_b = sprite_b.rect
    offset_x, offset_y = (rect_b.left - rect_a.left), (rect_b.top - rect_a.top)
    if(sprite_a.mask.overlap(sprite_b.mask, (offset_x, offset_y)) is not None):
        return True
    else:
        return False

def spawn_enemies(quantity):
    for x in range(quantity):
        print("enemy {}".format(x))
        print(Enemy(0, screen_height / 2, (random.randint(-1, 1), 1)))

def game_over():  # game over screen/menu?
    pygame.mouse.set_visible(True)
    global score
    game_over_text = Text("GAME OVER", 40, white).textSurf
    game_over_x    = screen_width / 2 - game_over_text.get_width() / 2
    score_text     = Text("Score: {}".format(score), 30, white).textSurf
    score_text_x   = screen_width / 2 - score_text.get_width() / 2
    again_text     = Text("Press Space", 30, green).textSurf
    again_text_x   = screen_width / 2 - again_text.get_width() / 2
    screen.blit(game_over_text, (game_over_x, screen_height / 3))
    screen.blit(score_text, (score_text_x, screen_height / 2))
    screen.blit(again_text, (again_text_x, screen_height / 1.5))
    pygame.display.flip()
    done = False
    while not done:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # perhaps I should add a "play again" button?
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    reset_game()
                if event.key in (pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass  # TODO add continue button.
                #print(again_text.get_rect())
                #print(mouse_y, mouse_x)
            # else:
            #    print(event, event.type)
            #    main()
        fpsClock.tick(60)

def reset_game():
    global score
    score = 0
    for s in all_sprites_list:
        all_sprites_list.remove(s)
    for s in p_bullet_sprites:
        p_bullet_sprites.remove(s)
    for s in enemy_group:
        enemy_group.remove(s)
    main()

player_sprite = Player(300, 500)
all_sprites_list = pygame.sprite.Group()
p_bullet_sprites = pygame.sprite.Group()
enemy_group      = pygame.sprite.Group()
spawn_enemies(10)

def main():
    pygame.mouse.set_visible(False)
    all_sprites_list.add(player_sprite)
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

        # pixel perfect collision player v enemy
        for sprite in enemy_group:
            if(pixel_collision(sprite, player_sprite)):
                game_over()
        # collision enemy vs bullets
        for bullet in p_bullet_sprites:
            for enemy in enemy_group:
                if(pixel_collision(bullet, enemy)):
                    global score
                    score = score + 1
                    enemy_group.remove(enemy)
                    p_bullet_sprites.remove(bullet)
                    all_sprites_list.remove(bullet, enemy)
                    test_sound.play()
            # TODO: add sound/animation?
            # TODO: spawn loot drops here at position of collision.

        # if enemies have been destroyed, lets spawn some new ones.
        # TODO: further complicate with level formula/speeds?
        timer = pygame.time.get_ticks() / 10000
        if len(enemy_group) < timer:
            spawn_enemies(2)

        # update all the things!
        all_sprites_list.update()

        # paint bg, clear the field.
        pygame.sprite.Group(lvl_one_bg).draw(screen)
        # draw all the things!
        all_sprites_list.draw(screen)
        screen.blit(Text("Score: {}".format(score)).textSurf, (20, 5))
        FPS_text = Text("FPS: {:.4}".format(fpsClock.get_fps())).textSurf
        screen.blit(FPS_text, (screen_width - FPS_text.get_width() - 20, 5))
        pygame.display.flip()  # reveal changes

        # slow it down, if necessary.
        fpsClock.tick(60)  # we don't need more than 60 fps for this. srsly.
main()
