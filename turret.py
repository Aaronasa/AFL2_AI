# turret.py

import pygame as pg
import math
import constants as c

class Turret(pg.sprite.Sprite):
  def __init__(self, sprite_sheet, tile_x, tile_y):
    pg.sprite.Sprite.__init__(self)
    self.range = 100
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

  # --- 1. MODIFIKASI FUNGSI UPDATE ---
  def update(self, enemy_group):
    reward = 0 # <-- Buat var reward
    
    # Cek jika target still alive
    if self.target and not self.target.alive():
      self.target = None 

    if self.target:
      reward = self.play_animation() # <-- Tangkap reward dari play_animation
    else:
      if pg.time.get_ticks() - self.last_shot > self.cooldown:
        self.pick_target(enemy_group)
        self.original_image = self.animation_list[0]
        
    return reward # <-- Kembalikan reward ke main.py
  # --- AKHIR MODIFIKASI ---

  def pick_target(self, enemy_group):
    best_enemy = None
    best_progress = (-1, float('inf')) 

    for enemy in enemy_group:
      x_dist = enemy.pos[0] - self.x
      y_dist = enemy.pos[1] - self.y
      dist_to_enemy = math.sqrt(x_dist ** 2 + y_dist ** 2)

      if dist_to_enemy < self.range:
        current_progress = (enemy.target_waypoint, enemy.remaining_dist)
        if current_progress[0] > best_progress[0]:
          best_enemy = enemy
          best_progress = current_progress
        elif current_progress[0] == best_progress[0]:
          if current_progress[1] < best_progress[1]:
            best_enemy = enemy
            best_progress = current_progress

    if best_enemy:
      self.target = best_enemy
      x_dist = self.target.pos[0] - self.x
      y_dist = self.target.pos[1] - self.y
      self.angle = math.degrees(math.atan2(-y_dist, x_dist))

# BUAT CHECK ACCURACY
      # try:
      #       from pathfinder import turret_accuracy_log
      #       turret_accuracy_log["total"] += 1
      #       # Benar jika turret memilih musuh dengan waypoint tertinggi (paling maju)
      #       is_correct = all(
      #           (e.target_waypoint <= best_enemy.target_waypoint)
      #           for e in enemy_group
      #           if math.sqrt((e.pos[0] - self.x)**2 + (e.pos[1] - self.y)**2) < self.range
      #       )
      #       if is_correct:
      #           turret_accuracy_log["correct"] += 1

      #       print(f"[Turret Accuracy] Correct={turret_accuracy_log['correct']}, Total={turret_accuracy_log['total']}")
      # except Exception as e:
      #       print("Error logging turret accuracy:", e)

  # --- 2. MODIFIKASI FUNGSI PLAY_ANIMATION ---
  def play_animation(self):
    reward = 0 # <-- Buat var reward
    self.original_image = self.animation_list[self.frame_index]
    
    if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
      self.update_time = pg.time.get_ticks()
      self.frame_index += 1
      
      if self.frame_index >= len(self.animation_list):
        self.frame_index = 0
        
        if self.target:
          reward = self.target.hit(self.damage) # <-- Tangkap reward dari hit()

        self.last_shot = pg.time.get_ticks()
        self.target = None
        
    return reward # <-- Kembalikan reward ke update()
  # --- AKHIR MODIFIKASI ---

  def draw(self, surface):
    self.image = pg.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)
    surface.blit(self.image, self.rect)
    if self.selected:
      surface.blit(self.range_image, self.range_rect)