# world.py

import pygame as pg

class World():
  # Hapus 'path_name' dari parameter __init__
  def __init__(self, data, map_image):
    self.waypoints = [] # Waypoints akan diisi oleh main.py
    self.level_data = data
    self.image = map_image
    self.tile_map = []
    # Hapus self.path_name

  def process_data(self):
    # Fungsi ini sekarang HANYA memproses tile_map
    for layer in self.level_data["layers"]:
      if layer["name"] == "Batu+Texturing":
        self.tile_map = layer["data"]

  def process_waypoints(self, data, offset_x, offset_y):
    for point in data:
      temp_x = point.get("x") + offset_x
      temp_y = point.get("y") + offset_y
      self.waypoints.append((temp_x, temp_y))

  def draw(self, surface):
    surface.blit(self.image, (0, 0))
