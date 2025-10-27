# main.py

import pygame as pg
import json
import random # <-- 1. IMPORT MODUL RANDOM
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
import constants as c
import pathfinder as pf 

#initialise pygame
pg.init()
text_font = pg.font.SysFont("Arial", 30)
clock = pg.time.Clock()

screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

#game variables
placing_turrets = False
selected_turret = None
last_enemy_spawn = pg.time.get_ticks() 
spawn_cooldown = 1000 
health = 1
money = 100 

# --- 2. MODIFIKASI LOAD IMAGES ---
# Load gambar turret, map, dll.
turret_sheet = pg.image.load('assets/turrets/turret_02_mk1_(1).png').convert_alpha()
map_image = pg.image.load('assets/map.jpeg').convert_alpha()
cursor_turret = pg.image.load('assets/turrets/mouse_turret_02_mk1.png').convert_alpha()
buy_turret_image = pg.image.load('assets/button/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/button/cancel.png').convert_alpha()

# Load gambar-gambar musuh
enemy_image_base = pg.image.load('assets/balloon/towerDefense_tile245.png').convert_alpha()
# Buat gambar musuh "Strong" (1.5x lebih besar)
image_strong = pg.transform.scale(enemy_image_base, (int(enemy_image_base.get_width() * 1.5), int(enemy_image_base.get_height() * 1.5)))
# --- AKHIR MODIFIKASI LOAD ---


# --- 3. BUAT DATA MUSUH ---
# Definisikan stats untuk setiap tipe musuh
enemy_data = {
    "regular": {"health": 2, "speed": 2, "reward": c.ENEMY_REWARD, "image": enemy_image_base},
    "strong": {"health": 10, "speed": 1, "reward": 50, "image": image_strong},
    "fast": {"health": 1, "speed": 4, "reward": 15, "image": enemy_image_base} # Pakai gambar yg sama dgn regular
}
# Tentukan musuh apa saja yang akan muncul
# (Lebih banyak "regular" dibanding yang lain)
spawn_list = ["regular", "regular", "regular", "regular", "fast", "fast", "strong"]
# --- AKHIR DATA MUSUH ---


with open('assets/level/Map+LineShortest.tmj') as file:
  world_data = json.load(file)

# Fungsi untuk menggambar teks
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

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
      return True 
  return False 

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
world = World(world_data, map_image) 
world.process_data() 

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

def recalculate_path():
  new_pixel_path, path_name = pf.choose_best_path(world_data, turret_group)
  world.waypoints = new_pixel_path
  for enemy in enemy_group:
    enemy.waypoints = new_pixel_path
  print(f"Path dihitung ulang, menggunakan: {path_name}") 

recalculate_path()

#create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
delete_button = Button(c.SCREEN_WIDTH + 50, 240, cancel_image, True) 

#game loop
run = True
while run:

  clock.tick(c.FPS)
  screen.fill("grey100")
  world.draw(screen)

  if world.waypoints:
    pg.draw.lines(screen, "red", False, world.waypoints)

  # --- 4. MODIFIKASI SPAWN ENEMIES ---
  if pg.time.get_ticks() - last_enemy_spawn > spawn_cooldown:
    if world.waypoints: 
      # 1. Pilih tipe musuh acak dari spawn_list
      enemy_type_name = random.choice(spawn_list)
      # 2. Ambil data stats musuh tersebut
      stats = enemy_data[enemy_type_name]
      # 3. Buat musuh baru dengan stats tersebut
      enemy = Enemy(
          world.waypoints, 
          stats["image"], 
          stats["health"], 
          stats["speed"], 
          stats["reward"]
      )
      enemy_group.add(enemy)
      last_enemy_spawn = pg.time.get_ticks() 
  # --- AKHIR MODIFIKASI SPAWN ---

  # Update enemies
  for enemy in enemy_group:
    reached_end = enemy.update()
    if reached_end:
      health -= 1 

  # Update turrets dan tambahkan uang
  for turret in turret_group:
    reward = turret.update(enemy_group)
    money += reward 

  #highlight selected turret
  if selected_turret:
    selected_turret.selected = True
    if delete_button.draw(screen):
      selected_turret.kill()
      selected_turret = None
      recalculate_path() 

  #draw groups
  enemy_group.draw(screen)
  for enemy in enemy_group:
    enemy.draw_health_bar(screen)
  for turret in turret_group:
    turret.draw(screen)

  # Tampilkan Teks UI
  draw_text(f"Health: {health}", text_font, (0, 0, 0), c.SCREEN_WIDTH + 10, 20)
  draw_text(f"Money: ${money}", text_font, (0, 0, 0), c.SCREEN_WIDTH + 10, 60) 

  #draw buttons
  if turret_button.draw(screen):
    if money >= c.TURRET_COST:
      placing_turrets = True
      selected_turret = None 
      clear_selection()
    else:
      print("Uang tidak cukup untuk membeli turret!")

  if placing_turrets == True:
    cursor_rect = cursor_turret.get_rect()
    cursor_pos = pg.mouse.get_pos()
    cursor_rect.center = cursor_pos
    if cursor_pos[0] <= c.SCREEN_WIDTH:
      screen.blit(cursor_turret, cursor_rect)
    if cancel_button.draw(screen):
      placing_turrets = False

  #event handler
  for event in pg.event.get():
    if event.type == pg.QUIT:
      run = False
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
      mouse_pos = pg.mouse.get_pos()
      if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
        selected_turret = None
        clear_selection()
        if placing_turrets == True:
          if money >= c.TURRET_COST:
            turret_was_placed = create_turret(mouse_pos)
            if turret_was_placed:
              money -= c.TURRET_COST 
              recalculate_path()
              placing_turrets = False 
          else:
             placing_turrets = False 
        else:
          selected_turret = select_turret(mouse_pos)

  #update display
  pg.display.flip()

pg.quit()