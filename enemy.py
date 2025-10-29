# enemy.py

import pygame as pg
from pygame.math import Vector2
import math
import constants as c

class Enemy(pg.sprite.Sprite):
  # --- 1. MODIFIKASI __init__ ---
  # Tambahkan health, speed, dan reward sebagai parameter
  def __init__(self, waypoints, image, health, speed, reward):
    pg.sprite.Sprite.__init__(self)
    self.waypoints = waypoints
    self.pos = Vector2(self.waypoints[0])
    self.target_waypoint = 1
    self.speed = speed # <-- Gunakan parameter
    self.angle = 0
    self.original_image = image
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos
    self.remaining_dist = 0
    self.max_health = health # <-- Gunakan parameter
    self.health = self.max_health 
    self.reward = reward # <-- Simpan reward

  def update(self):
    reached_end = self.move()
    self.rotate()
    return reached_end

  def move(self):
    #define a target waypoint
    if self.target_waypoint < len(self.waypoints):
      self.target = Vector2(self.waypoints[self.target_waypoint])
      self.movement = self.target - self.pos
    else:
      #enemy has reached the end of the path
      self.remaining_dist = 0
      self.kill()
      return True 

    #calculate distance to target
    dist = self.movement.length()
    self.remaining_dist = dist
    
    #check if remaining distance is greater than the enemy speed
    if dist >= self.speed:
      self.pos += self.movement.normalize() * self.speed
    else:
      if dist != 0:
        self.pos += self.movement.normalize() * dist
      self.target_waypoint += 1

    return False 

  def rotate(self):
    if not hasattr(self, 'target'):
        return 
    dist = self.target - self.pos
    self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos

  # --- 2. MODIFIKASI FUNGSI HIT ---
  def hit(self, damage):
    self.health -= damage
    if self.health <= 0:
      self.kill() 
      return self.reward # <-- Kembalikan reward yang disimpan
    return 0 
  # --- AKHIR MODIFIKASI ---

  def draw_health_bar(self, surface):
    if self.health < self.max_health:
      bar_width = 40
      bar_height = 5
      # Posisi bar kesehatan akan otomatis menyesuaikan di atas musuh
      x = self.pos.x - (bar_width / 2)
      y = self.pos.y - (self.rect.height / 2) - 10 
      
      health_percent = self.health / self.max_health
      
      pg.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
      pg.draw.rect(surface, (0, 255, 0), (x, y, bar_width * health_percent, bar_height))