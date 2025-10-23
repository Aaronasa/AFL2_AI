import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
import constants as c

#initialise pygame
pg.init()

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

#game variables
placing_turrets = False
selected_turret = None
last_enemy_spawn = pg.time.get_ticks() # <-- TAMBAHKAN
spawn_cooldown = 1000 # (1000ms = 1 detik) <-- TAMBAHKAN

#load images
#turret spritesheets
turret_sheet = pg.image.load('assets/turrets/turret_02_mk1_(1).png').convert_alpha()
#map
map_image = pg.image.load('assets/map.jpeg').convert_alpha()
#turrets
cursor_turret = pg.image.load('assets/turrets/mouse_turret_02_mk1.png').convert_alpha()
#enemies
enemy_image = pg.image.load('assets/balloon/towerDefense_tile245.png').convert_alpha()
#buttons
buy_turret_image = pg.image.load('assets/button/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/button/cancel.png').convert_alpha()

#load json data for level
with open('assets/level/Map+LineShortest.tmj') as file:
  world_data = json.load(file)

def create_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  if world.tile_map[mouse_tile_num] in c.BUILDABLE_TILES:
    space_is_free = True
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        space_is_free = False
    if space_is_free == True:
      new_turret = Turret(turret_sheet, mouse_tile_x, mouse_tile_y)
      turret_group.add(new_turret)

def select_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  for turret in turret_group:
    if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
      return turret

def clear_selection():
  for turret in turret_group:
    turret.selected = False

#create world
world = World(world_data, map_image, "Shortest") 
world.process_data()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)

#game loop
run = True
while run:

  clock.tick(c.FPS)

  screen.fill("grey100")

  #draw level
  world.draw(screen)

  pg.draw.lines(screen, "red", False, world.waypoints)

  if pg.time.get_ticks() - last_enemy_spawn > spawn_cooldown:
    enemy = Enemy(world.waypoints, enemy_image)
    enemy_group.add(enemy)
    last_enemy_spawn = pg.time.get_ticks() # reset timer

  #update groups
  enemy_group.update()
  turret_group.update(enemy_group)

  #highlight selected turret
  if selected_turret:
    selected_turret.selected = True

  #draw groups
  enemy_group.draw(screen)
  for turret in turret_group:
    turret.draw(screen)

    #draw buttons
  #button for placing turrets
  if turret_button.draw(screen):
    placing_turrets = True
  #if placing turrets then show the cancel button as well
  if placing_turrets == True:
    #show cursor turret
    cursor_rect = cursor_turret.get_rect()
    cursor_pos = pg.mouse.get_pos()
    cursor_rect.center = cursor_pos
    if cursor_pos[0] <= c.SCREEN_WIDTH:
      screen.blit(cursor_turret, cursor_rect)
    if cancel_button.draw(screen):
      placing_turrets = False

  #event handler
  for event in pg.event.get():
    #quit program
    if event.type == pg.QUIT:
      run = False
    #mouse click
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
      mouse_pos = pg.mouse.get_pos()
      #check if mouse is on the game area
      if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
        #clear selected turrets
        selected_turret = None
        clear_selection()
        if placing_turrets == True:
          create_turret(mouse_pos)
        else:
          selected_turret = select_turret(mouse_pos)

  #update display
  pg.display.flip()

pg.quit()