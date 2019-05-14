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

# pygame.init mysteriously crashes on debian when pygame.quit is called.
# lets use pygame.display instead, and hope that doesn't cause issues.
pygame.display.init()
pygame.font.init()   # it caused issues. required for text.
pygame.mixer.init()  # for sound

# in case we're running the game from a shortcut or remotely or somethin
# lets cd to the project dir so relative filenames work
#os.chdir(os.path.dirname(__file__))

test_sound_file = './assets/drip.ogg'
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
screen = pygame.display.set_mode((640, 960))
screen_width = screen.get_width()
screen_height = screen.get_height()
pygame.display.set_caption('SPAAACE bubbles!')

all_sprites_list = pygame.sprite.Group()
p_bullet_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

all_sprites_list = pygame.sprite.Group()
p_bullet_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
upgrade_group = pygame.sprite.Group()



#########################################
# CLASSES
#########################################


class S_Picture(pygame.sprite.Sprite):

    def __init__(self, image_filename, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_filename).convert_alpha()
        # rotation of images causes deformation.
        # keep origin on file for reference.
        self.origin_img = self.image
        self.rect = self.image.get_rect()
        self.rect.x = location[0]
        self.rect.y = location[1]
        self.mask = pygame.mask.from_surface(self.image)
        self.frames_alive = 0
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()
        # enemies, player, bullets, etc. they all need health pools.
        self.health = 4

    def move(self, location):
        self.rect.x = location[0]
        self.rect.y = location[1]

    def update(self):
        self.frames_alive += 1


class Player(S_Picture):

    def __init__(self, location):
        S_Picture.__init__(self, self.image_filename, location)
    image_filename = './assets/SpaceShip.png'
    bullet_type = 0  # default type....this seems cryptic. #TODO #FIXME



player_sprite = Player((300, 500))


class Bullet(S_Picture):
    # TODO: seriously need a better solution here than lambdas.
    # bullet_types = [{'filename': './assets/player_bullet.png',  # default
    #                  'formula x': lambda x, s: s,   # horizontal trajectory
    #                  'formula y': lambda y: y - 8,  # vertical trajectory
    #                  # degrees for angle transform. 0 = no change.
    #                  'formula d': lambda d: 0,
    #                  'health': 1},
    #                  {'filename' : './assets/bullet_2.png',
    #                  lambda current_x, spawn_x
    #                  'formula x': lambda x, s: s + math.sin(x) *
    #                  (screen_width / 20),  # pep8 pls ;_;
    #                  'formula y': lambda y: y - 8,
    #                  'formula d': lambda d: 0,
    #                  'health'   : 1},
    #                 # #this one is aweful. gamebreaking aweful.
    #                 # {'filename' : './assets/wave_bullet.png',
    #                 #  # lambda current_x, spawn_x
    #                 #  'formula x': lambda x, s: s + math.sin(x) *
    #                 #  (screen_width / 20),  # pep8 pls ;_;
    #                 #  'formula y': lambda y: y - 8,
    #                 #  'formula d': lambda d: 0,
    #                 #  'health'   : 3}
    #                 ]

    # x, y for initial spawn location
    # hostile to be True or False. hostile = dmg to player.
    # bullet_type to be referenced for:
    # bullet img file name
    # bullet trajectory formula choice and calculations
    def __init__(self, location, hostile=False, behavior=lambda b: b, image_filename='./assets/scary_bubbles.png'):
        # default behavior is to not move.
        self.spawn_location = location
        self.hostile = hostile
        self.image_filename = image_filename
        S_Picture.__init__(self, self.image_filename, location)
        self.health = 1 # 

    def update(self):
        # x_formula = self.bullet_types[self.bullet_type]['formula x']
        # y_formula = self.bullet_types[self.bullet_type]['formula y']
        # d = delta for the angle of the bullet
        # d_formula = self.bullet_types[self.bullet_type]['formula d']
        #self.image = pygame.transform.rotate(self.origin_img,
        #                                     d_formula(self.rect.y))
        super().update()
        self.move(self.behavior(self.frames_alive+1))
        # self.rect.x = x_formula(
        #     self.rect.y, self.spawn_x) - self.image_width / 2
        # self.rect.y = y_formula(self.rect.y)
        if self.rect.y < 0:  # destroy sprite if it's out of range.
            p_bullet_sprites.remove(self)
            all_sprites_list.remove(self)


class Enemy(S_Picture):

    def __init__(self, location, vector=(0, 1)):
        S_Picture.__init__(self, self.image_filename, location)
        self.v_x, self.v_y = vector
        self.relocate()  # find a good initial position.
        self.health = 2
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
        if self.rect.x < 0 - self.image_width:
            self.rect.x = screen_width

    def relocate(self):
        attempts = 0
        # keep trying to find a free spot. give it a few tries.
        enemy_group.remove(self)  # if it already exists = inf collision
        self.rect.x = get_rand_x()
        self.rect.y = 0
        while(pygame.sprite.spritecollide(self, enemy_group, False)):
            attempts = attempts + 1
            # prevent inf loop by repositioning in y
            # FIXME: does this actually prevent inf loop? or just
            # make a train along the y axis?
            if attempts > 10:
                self.rect.y = self.rect.y - 20
        enemy_group.add(self)


class Upgrade(S_Picture):
    image_filename = './assets/upgrade_cir.png'

    def __init__(self, x, y):
        self.upgrade_type = 0  # TODO: diff types of upgrade
        S_Picture.__init__(self, self.image_filename, x, y)
        all_sprites_list.add(self)
        upgrade_group.add(self)


class Bg_Picture(S_Picture):

    def __init__(self, image_filename):
        self.image_filename = image_filename
        S_Picture.__init__(self, self.image_filename, (0, -1782 + screen_height))


class Text(pygame.sprite.Sprite):

    def __init__(self, text, size=16, color=WHITE, width=40, height=40):
        # this object doesn't use width or height? FIXME?
        pygame.sprite.Sprite.__init__(self)

        self.font = pygame.font.SysFont("Arial", size)
        self.textSurf = self.font.render(text, 1, color)



lvl_one_bg = Bg_Picture('./assets/level one.png')

##############################
# function definitions
#############################


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
        Enemy(location=(0, screen_height / 2), vector=(random.randint(-1, 1), 1))

def spawn_bullet(mouseLocation):
    mouse_x, mouse_y = mouseLocation
    new_bullet = Bullet(
        location=(mouse_x, mouse_y - player_sprite.image_height / 2), hostile=False)
    p_bullet_sprites.add(new_bullet)
    all_sprites_list.add(new_bullet)

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
                    reset_game()
                if event.key is pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass  # TODO add continue button.
                # print(again_text.get_rect())
                # print(mouse_y, mouse_x)
            # else:
            #    print(event, event.type)
            #    main()
        fpsClock.tick(15)


def reset_game():
    global score
    score = 0
    global start_time
    start_time = time.time()
    for s in all_sprites_list: # can i not just purge these lists?
        all_sprites_list.remove(s)
    for s in p_bullet_sprites:
        p_bullet_sprites.remove(s)
    for s in enemy_group:
        enemy_group.remove(s)
    for s in upgrade_group:
        upgrade_group.remove(s)
    main()



# spawn_enemies(10)


def main():
    pygame.mouse.set_visible(False)
    all_sprites_list.add(player_sprite)
    done = False
    mouse_button_pressed = False
    bullet_delay = 3  # allow a bullet fired every N frames
    bullet_timer = bullet_delay
    while not done:  # main loop
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.K_ESCAPE):
                done = True

            # TODO: add keyboard controls here.
            # mouse controls
            elif event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                # put center of ship on mouse, not corner of picture.
                player_sprite.rect.x = x - player_sprite.image_width / 2
                player_sprite.rect.y = y - player_sprite.image_height / 2

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_button_pressed = False
        if mouse_button_pressed is True:  # auto fire
            if bullet_timer == 0:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # FIXME: should be a spawn_sprite(location) method.
                spawn_bullet((mouse_x, mouse_y))
                bullet_timer = bullet_delay
            else:
                bullet_timer = bullet_timer - 1

        # pixel perfect collision player v enemy
        for sprite in enemy_group:
            if(pixel_collision(sprite, player_sprite)):
                # this is where the health bar comes in?
                game_over()

        # collision enemy vs bullets
        for bullet in p_bullet_sprites:
            for enemy in enemy_group:
                if(pixel_collision(bullet, enemy)):
                    # deal damage to both parties.
                    temp = enemy.health
                    enemy.health = enemy.health - bullet.health
                    bullet.health = bullet.health - temp
                    # parsing out the consequences.
                    if enemy.health <= 0:  # enemy death
                        enemy_group.remove(enemy)
                        all_sprites_list.remove(enemy)
                        global score
                        score = score + 1
                        test_sound.play()
                        # upgrade spawn at random chance
                        if(random.randrange(30) > 25):
                            # upgrades are complicated. lets readd later.
                            # Upgrade(enemy.rect.x, enemy.rect.y)
                            pass
                    if bullet.health <= 0:  # bullet death
                        p_bullet_sprites.remove(bullet)
                        all_sprites_list.remove(bullet)
            # TODO: add sound/animation?

        # collision player v upgrades
        for upgrade in upgrade_group:
            if(pixel_collision(player_sprite, upgrade)):
                upgrade_group.remove(upgrade)
                all_sprites_list.remove(upgrade)
                # player_sprite.bullet_type + 1
                if player_sprite.bullet_type < 2:
                    player_sprite.bullet_type = player_sprite.bullet_type + 1

        # if enemies have been destroyed, lets spawn some new ones.
        # TODO: further complicate with level formula/speeds/balance
        timer = int(time.time() - start_time)

        if len(enemy_group) < timer + 1 / (1 + sum(range(1, timer))):
            spawn_enemies(2)
        # print("timer: {} {}".format(start_time, timer))
        # print("Currently {} enemies fielded.".format(len(enemy_group)))
        # print("all sprites:  {}".format(len(all_sprites_list)))
        # update all the things!
        all_sprites_list.update()

        # paint bg, clear the field.
        pygame.sprite.Group(lvl_one_bg).draw(screen)
        # draw all the things!
        all_sprites_list.draw(screen)
        screen.blit(Text("Score: {}".format(score)).textSurf, (20, 5))
        FPS_text = Text("FPS: {:.4}".format(fpsClock.get_fps())).textSurf
        screen.blit(FPS_text, (screen_width - FPS_text.get_width() - 20, 5))

        global high_score
        if high_score <= score:
            high_score = score

        High_score_text = Text("High Score: {}".format(
            high_score)).textSurf  # pep8 pls ;_;
        screen.blit(High_score_text, ((screen_width / 2 -
                                       High_score_text.get_width() / 2), 5))
        pygame.display.flip()  # reveal changes

        # slow it down, if necessary.
        fpsClock.tick(60)  # we don't need more than 60 fps for this. srsly.


main()
