# main.py

import pygame as pg
import random
import math # <-- Pastikan ini ada (dibutuhkan untuk recalculate_path)
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
import constants as c
import pathfinder as pf 

# 1. Inisialisasi modul-modul Pygame
pg.init() 

# 2. BUAT JENDELA (LAYAR) UTAMA
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

# 3. SETELAH layar dibuat, baru inisialisasi hal lain
text_font = pg.font.SysFont("Arial", 30)
debug_font = pg.font.SysFont("Arial", 14, bold=True)
clock = pg.time.Clock()

#game variables
placing_turrets = False
selected_turret = None
last_enemy_spawn = pg.time.get_ticks() 
spawn_cooldown = 1000 
health = 100
money = 1000

# --- MODIFIKASI LOAD IMAGES (Bagian 1) ---
try:
    grass_image = pg.image.load('assets/grass.jpeg').convert_alpha()
    path_image = pg.image.load('assets/path.jpeg').convert_alpha()
    start_image = pg.image.load('assets/start.jpeg').convert_alpha()
    end_image = pg.image.load('assets/end.jpeg').convert_alpha()
except pg.error as e:
    print(f"Error loading tile images: {e}")
    grass_image = pg.Surface((c.TILE_SIZE, c.TILE_SIZE)); grass_image.fill((0, 100, 0))
    path_image = pg.Surface((c.TILE_SIZE, c.TILE_SIZE)); path_image.fill((100, 100, 100))
    start_image = pg.Surface((c.TILE_SIZE, c.TILE_SIZE)); start_image.fill((255, 255, 255))
    end_image = pg.Surface((c.TILE_SIZE, c.TILE_SIZE)); end_image.fill((0, 0, 0))

# Buat dictionary untuk tile
tile_images = {
    c.BUILDABLE_TILE_ID: grass_image,
    c.PATH_TILE_ID: path_image,
    c.START_TILE_ID: start_image,
    c.END_TILE_ID: end_image
}
# --- AKHIR MODIFIKASI LOAD (Bagian 1) ---

# --- DI SINI PERBAIKANNYA (VERSI BARU) ---
# Hapus: BLACK = (0, 0, 0) dan WHITE = (255, 255, 255)

# Load gambar turret, cursor, button
turret_sheet = pg.image.load('assets/turrets/turret_02_mk1_(1).png').convert_alpha()
# GANTI: turret_sheet.set_colorkey(BLACK)
# MENJADI: (Baca warna di pixel (0,0) dan jadikan transparan)
turret_sheet.set_colorkey(turret_sheet.get_at((0, 0))) 

cursor_turret = pg.image.load('assets/turrets/mouse_turret_02_mk1.png').convert_alpha()
# GANTI: cursor_turret.set_colorkey(BLACK)
# MENJADI:
cursor_turret.set_colorkey(cursor_turret.get_at((0, 0)))

buy_turret_image = pg.image.load('assets/button/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/button/cancel.png').convert_alpha()

# Load gambar enemy dan data enemy
enemy_image_base = pg.image.load('assets/balloon/towerDefense_tile245.png').convert_alpha()
# GANTI: enemy_image_base.set_colorkey(WHITE)
# MENJADI:
enemy_image_base.set_colorkey(enemy_image_base.get_at((0, 0)))

image_strong = pg.transform.scale(enemy_image_base, (int(enemy_image_base.get_width() * 1.5), int(enemy_image_base.get_height() * 1.5)))
# GANTI: image_strong.set_colorkey(WHITE)
# MENJADI: (Kita set colorkey-nya DARI GAMBAR ASLI)
image_strong.set_colorkey(enemy_image_base.get_at((0, 0)))
# --- AKHIR PERBAIKAN ---

enemy_data = {
    "regular": {"health": 2, "speed": 2, "reward": c.ENEMY_REWARD, "image": enemy_image_base},
    "strong": {"health": 10, "speed": 1, "reward": 50, "image": image_strong},
    "fast": {"health": 1, "speed": 4, "reward": 15, "image": enemy_image_base}
}
spawn_list = ["regular", "regular", "regular", "regular", "fast", "fast", "strong"]


# ... (Fungsi draw_text, create_turret, select_turret, clear_selection tetap SAMA) ...
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def create_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  if mouse_tile_num >= len(world.tile_map):
      return False
  if world.tile_map[mouse_tile_num] == c.BUILDABLE_TILE_ID:
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
# --- AKHIR FUNGSI YG TETAP SAMA ---


#create world
world = World("assets/level/map_layout.txt", tile_images) 
world.process_data() # Ini akan membaca .txt dan mencari Start/End

background_surface = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
world.draw(background_surface) 

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

# --- MODIFIKASI TOTAL recalculate_path ---
def recalculate_path():
  print("Mencari path baru (mempertimbangkan bahaya)...")
  
  # 1. Kumpulkan semua posisi turret (sebagai obstacle/tembok)
  turret_tiles = set()
  for turret in turret_group:
    turret_tiles.add((turret.tile_x, turret.tile_y))

  # 2. Buat "Danger Map"
  danger_zones = set()
  for turret in turret_group:
    tr = turret.tile_range
    for y in range(max(0, turret.tile_y - tr), min(c.ROWS, turret.tile_y + tr + 1)):
      for x in range(max(0, turret.tile_x - tr), min(c.COLS, turret.tile_x + tr + 1)):
        tile_center_x = (x + 0.5) * c.TILE_SIZE
        tile_center_y = (y + 0.5) * c.TILE_SIZE
        dist = math.sqrt((turret.x - tile_center_x)**2 + (turret.y - tile_center_y)**2)
        
        if dist <= turret.range:
          danger_zones.add((x, y))

  # 3. Cari path menggunakan A*
  path_tiles = pf.find_path(
      world.tile_map, 
      world.start_tile_pos, 
      world.end_tile_pos, 
      turret_tiles,
      danger_zones # Argumen baru
  )
  
  if path_tiles:
    print(f"✅ Path ditemukan! Panjang: {len(path_tiles)} tiles.")
    world.convert_path_to_pixels(path_tiles)
  else:
    print("❌ PERINGATAN: Tidak ada path! Musuh tidak bisa bergerak.")
    world.waypoints = [] # Kosongkan waypoints
# --- AKHIR MODIFIKASI recalculate_path ---

# Hitung path pertama kali saat game dimulai
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

  # --- OPTIMASI 2: GAMBAR BACKGROUND ---
  screen.blit(background_surface, (0, 0))
  # --- AKHIR OPTIMASI 2 ---


  # Gambar path (untuk debug)
  if world.waypoints:
    pg.draw.lines(screen, "red", False, world.waypoints, 2)

  # --- MODIFIKASI SPAWN ENEMIES ---
  if pg.time.get_ticks() - last_enemy_spawn > spawn_cooldown:
    if world.waypoints: 
      enemy_type_name = random.choice(spawn_list)
      stats = enemy_data[enemy_type_name]
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

  # ... (Update enemies, Update turrets tetap SAMA) ...
  for enemy in enemy_group:
    reached_end = enemy.update()
    if reached_end:
      health -= 1 

  for turret in turret_group:
    reward = turret.update(enemy_group)
    money += reward 

  # --- MODIFIKASI delete_button ---
  if selected_turret:
    selected_turret.selected = True
    if delete_button.draw(screen):
      selected_turret.kill()
      selected_turret = None
      recalculate_path() # <-- Panggil ini saat turret dihapus
  # --- AKHIR MODIFIKASI ---

  #draw groups
  enemy_group.draw(screen)
  for enemy in enemy_group:
    enemy.draw_health_bar(screen)
  for turret in turret_group:
    turret.draw(screen)

  # ... (Tampilkan Teks UI, Cek Game Over, Draw Buttons tetap SAMA) ...
  draw_text(f"Health: {health}", text_font, (0, 0, 0), c.SCREEN_WIDTH + 10, 20)
  draw_text(f"Money: ${money}", text_font, (0, 0, 0), c.SCREEN_WIDTH + 10, 60) 

  if health <= 0:
    run = False
    print("GAME OVER!.")

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
  
  # --- MODIFIKASI Event Handler ---
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
  # --- AKHIR MODIFIKASI ---

  pg.display.flip()

pg.quit()