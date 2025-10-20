import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
import constants as c

#initialise pygame
pg.init()

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

#load images
#map
map_image = pg.image.load('assets/map.jpeg').convert_alpha()
#turrets
cursor_turret = pg.image.load('assets/turrets/mouse_turret_02_mk1.png').convert_alpha()
#enemies
enemy_image = pg.image.load('assets/balloon/towerDefense_tile245.png').convert_alpha()

#load json data for level
with open('assets/level/MAP+TRIAL.tmj') as file:
  world_data = json.load(file)

BUILDABLE_TILES = [489, 490, 550, 551]

def create_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  if world.tile_map[mouse_tile_num] in BUILDABLE_TILES:
    space_is_free = True
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        space_is_free = False
    if space_is_free == True:
      new_turret = Turret(cursor_turret, mouse_tile_x, mouse_tile_y)
      turret_group.add(new_turret)

#create world
world = World(world_data, map_image, "Shortest") 
world.process_data()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

enemy = Enemy(world.waypoints, enemy_image)
enemy_group.add(enemy)

#game loop
run = True
while run:

  clock.tick(c.FPS)

  screen.fill("grey100")

  #draw level
  world.draw(screen)

  pg.draw.lines(screen, "red", False, world.waypoints)

  #update groups
  enemy_group.update()
  turret_group.update()

  #draw groups
  enemy_group.draw(screen)
  turret_group.draw(screen)

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
        create_turret(mouse_pos)

  #update display
  pg.display.flip()

pg.quit()