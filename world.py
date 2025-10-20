# world.py

import pygame as pg

class World():
  # Tambahkan 'path_name' sebagai parameter
  def __init__(self, data, map_image, path_name):
    self.waypoints = []
    self.level_data = data
    self.image = map_image
    self.tile_map = []
    self.path_name = path_name # Simpan nama path

  def process_data(self):
    for layer in self.level_data["layers"]:
      if layer["name"] == "Batu+Texturing":
        self.tile_map = layer["data"]
      # Gunakan variabel self.path_name, bukan string "Shortest"
      if layer["name"] == self.path_name:
        for obj in layer["objects"]:
          waypoint_data = obj["polyline"]
          offset_x = obj["x"]
          offset_y = obj["y"]
          self.process_waypoints(waypoint_data, offset_x, offset_y)

  def process_waypoints(self, data, offset_x, offset_y):
    for point in data:
      temp_x = point.get("x") + offset_x
      temp_y = point.get("y") + offset_y
      self.waypoints.append((temp_x, temp_y))

  def draw(self, surface):
    surface.blit(self.image, (0, 0))