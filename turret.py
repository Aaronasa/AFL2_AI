# turret.py (VERSI OPTIMAL - ANTI LAG)

import pygame as pg
import math
import constants as c

class Turret(pg.sprite.Sprite):
  def __init__(self, sprite_sheet, tile_x, tile_y):
    pg.sprite.Sprite.__init__(self)
    self.range = 50 # <-- Anda mengubah ini jadi 50, sudah saya sesuaikan
    self.cooldown = 500 
    self.damage = 1 
    self.last_shot = pg.time.get_ticks()
    self.selected = False
    self.target = None

    #position variables
    self.tile_x = tile_x
    self.tile_y = tile_y
    self.x = (self.tile_x + 0.5) * c.TILE_SIZE
    self.y = (self.tile_y + 0.5) * c.TILE_SIZE

    # --- 1. TAMBAHAN UNTUK OPTIMASI ---
    # Diperlukan untuk pg.sprite.collide_circle
    self.radius = self.range 
    # --- AKHIR TAMBAHAN ---

    self.tile_range = math.ceil(self.range / c.TILE_SIZE)

    #animation variables
    self.sprite_sheet = sprite_sheet
    self.animation_list = self.load_images()
    self.frame_index = 0
    self.update_time = pg.time.get_ticks()

    self.angle = 90
    self.original_image = self.animation_list[self.frame_index]
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)

    # range image (sudah benar)
    self.range_image = pg.Surface((self.range * 2, self.range * 2))
    self.range_image.fill((0, 0, 0))
    self.range_image.set_colorkey((0, 0, 0))
    pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
    self.range_image.set_alpha(100)
    self.range_rect = self.range_image.get_rect()
    self.range_rect.center = self.rect.center

  def load_images(self):
    size = self.sprite_sheet.get_height()
    animation_list = []
    for x in range(c.ANIMATION_STEPS):
      temp_img = self.sprite_sheet.subsurface(x * size, 0, size, size)
      animation_list.append(temp_img)
    return animation_list

  # Fungsi update (tetap sama)
  def update(self, enemy_group):
    reward = 0 
    
    if self.target and not self.target.alive():
      self.target = None 

    if self.target:
      reward = self.play_animation() 
    else:
      if pg.time.get_ticks() - self.last_shot > self.cooldown:
        self.pick_target(enemy_group)
        self.original_image = self.animation_list[0]
        
    return reward 

  # --- 2. FUNGSI pick_target (VERSI OPTIMAL / CEPAT) ---
  def pick_target(self, enemy_group):
    best_enemy = None
    best_progress = (-1, float('inf')) 

    # 1. Gunakan collide_circle untuk mendapatkan DAFTAR musuh di jangkauan
    # Ini JAUH LEBIH CEPAT daripada me-loop semua musuh
    enemies_in_range = pg.sprite.spritecollide(self, enemy_group, False, pg.sprite.collide_circle)

    if not enemies_in_range:
      return # Tidak ada musuh, selesai.

    # 2. Sekarang, loop HANYA musuh yang ada di jangkauan
    for enemy in enemies_in_range:
      # Kita tidak perlu cek jarak lagi, kita HANYA cek progres-nya
      current_progress = (enemy.target_waypoint, enemy.remaining_dist)
      
      if current_progress[0] > best_progress[0]:
        best_enemy = enemy
        best_progress = current_progress
      elif current_progress[0] == best_progress[0]:
        if current_progress[1] < best_progress[1]:
          best_enemy = enemy
          best_progress = current_progress

    # 3. Jika kita punya target terbaik, kunci targetnya
    if best_enemy:
      self.target = best_enemy
      x_dist = self.target.pos[0] - self.x
      y_dist = self.target.pos[1] - self.y
      self.angle = math.degrees(math.atan2(-y_dist, x_dist))
  # --- AKHIR PERUBAHAN ---

  # Fungsi play_animation (tetap sama)
  def play_animation(self):
    reward = 0 
    self.original_image = self.animation_list[self.frame_index]
    
    if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
      self.update_time = pg.time.get_ticks()
      self.frame_index += 1
      
      if self.frame_index >= len(self.animation_list):
        self.frame_index = 0
        
        if self.target:
          reward = self.target.hit(self.damage) 

        self.last_shot = pg.time.get_ticks()
        self.target = None
        
    return reward 

  # Fungsi draw (tetap sama)
  def draw(self, surface):
    self.image = pg.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)
    surface.blit(self.image, self.rect)
    if self.selected:
      surface.blit(self.range_image, self.range_rect)