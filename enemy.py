# enemy.py

import pygame as pg
from pygame.math import Vector2
import math
import constants as c

class Enemy(pg.sprite.Sprite):
  # --- 1. MODIFIKASI __init__ ---
  # Hapus 'path_name'
  def __init__(self, waypoints, image, health, speed, reward):

    """
    Args:
      waypoints: List koordinat path yang akan dilalui
      ... (sisa args) ...
      path_name: Dihapus
    """
    
    pg.sprite.Sprite.__init__(self)
    self.waypoints = waypoints
    self.pos = Vector2(self.waypoints[0])
    self.target_waypoint = 1
    self.speed = speed
    self.angle = 0
    self.original_image = image
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos
    self.remaining_dist = 0
    self.max_health = health
    self.health = self.max_health 
    self.reward = reward
    # Hapus self.committed_path

  def update(self):
    # ... (sisa fungsi update, move, rotate, hit tetap SAMA) ...
    reached_end = self.move()
    self.rotate()
    return reached_end

  def move(self):
    if self.target_waypoint < len(self.waypoints):
      self.target = Vector2(self.waypoints[self.target_waypoint])
      self.movement = self.target - self.pos
    else:
      self.remaining_dist = 0
      self.kill()
      return True 

    dist = self.movement.length()
    self.remaining_dist = dist
    
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

  def hit(self, damage):
    self.health -= damage
    if self.health <= 0:
      self.kill() 
      return self.reward 
    return 0 
 
  # --- 2. HAPUS FUNGSI draw_path_name ---
  # def draw_path_name(self, surface, font): ...
  # (Hapus seluruh fungsi ini)

  def draw_health_bar(self, surface):
    # ... (Fungsi ini tetap SAMA) ...
    if self.health < self.max_health:
      bar_width = 40
      bar_height = 5
      x = self.pos.x - (bar_width / 2)
      y = self.pos.y - (self.rect.height / 2) - 10 
      health_percent = self.health / self.max_health
      pg.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
      pg.draw.rect(surface, (0, 255, 0), (x, y, bar_width * health_percent, bar_height))