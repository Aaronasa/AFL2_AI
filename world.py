# world.py

import pygame as pg
import constants as c

class World():
  def __init__(self, layout_filepath, tile_images):
    self.waypoints = []
    self.layout_filepath = layout_filepath
    self.tile_images = tile_images
    self.tile_map = []
    
    # --- TAMBAHKAN INI ---
    self.start_tile_pos = None # (x, y)
    self.end_tile_pos = None   # (x, y)
    # --- AKHIR TAMBAHAN ---

    # Hapus self.current_path_name, tidak relevan lagi

  def process_data(self):
    try:
      with open(self.layout_filepath, 'r') as file:
        y = 0 # <-- Lacak baris (y)
        for line in file:
          row = line.strip().split()
          if row:
            x = 0 # <-- Lacak kolom (x)
            for tile_str in row:
              tile_id = int(tile_str)
              
              # --- TAMBAHKAN LOGIKA INI ---
              if tile_id == c.START_TILE_ID:
                self.start_tile_pos = (x, y)
              elif tile_id == c.END_TILE_ID:
                self.end_tile_pos = (x, y)
              # --- AKHIR TAMBAHAN ---
              
              self.tile_map.append(tile_id)
              x += 1
            y += 1
            
      if len(self.tile_map) != c.ROWS * c.COLS:
        print(f"WARNING: map layout file salah ukuran!")
      
      if not self.start_tile_pos:
        print("ERROR: Titik START (ID 2) tidak ditemukan di map_layout.txt")
      if not self.end_tile_pos:
        print("ERROR: Titik END (ID 3) tidak ditemukan di map_layout.txt")
        
    except Exception as e:
      print(f"FATAL ERROR: Tidak bisa loading map layout: {e}")
      self.tile_map = [c.BUILDABLE_TILE_ID] * (c.ROWS * c.COLS)
  
  # HAPUS FUNGSI process_waypoints(self, data, offset_x, offset_y)
  # Sudah tidak dipakai lagi.

  # --- TAMBAHKAN FUNGSI BARU INI ---
  def convert_path_to_pixels(self, path_tiles):
    """
    Mengubah list [(x1, y1), (x2, y2)] menjadi list pixel.
    Pixel berada di TENGAH tile.
    """
    pixel_waypoints = []
    for tile_pos in path_tiles:
        pixel_x = (tile_pos[0] * c.TILE_SIZE) + (c.TILE_SIZE / 2)
        pixel_y = (tile_pos[1] * c.TILE_SIZE) + (c.TILE_SIZE / 2)
        pixel_waypoints.append((pixel_x, pixel_y))
    self.waypoints = pixel_waypoints
  # --- AKHIR FUNGSI BARU ---

  def draw(self, surface):
    for y in range(c.ROWS):
      for x in range(c.COLS):
        tile_index = (y * c.COLS) + x
        if tile_index < len(self.tile_map):
          tile_id = self.tile_map[tile_index]
          image = self.tile_images.get(tile_id)
          if image:
            surface.blit(image, (x * c.TILE_SIZE, y * c.TILE_SIZE))
          else:
            pg.draw.rect(surface, (255, 0, 255), (x * c.TILE_SIZE, y * c.TILE_SIZE, c.TILE_SIZE, c.TILE_SIZE))