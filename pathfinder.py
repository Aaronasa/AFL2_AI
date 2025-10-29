# pathfinder.py
import math
import json
import pygame as pg
import constants as c # Impor constants untuk TILE_SIZE

# ==== Hitung turret di sekitar titik (TILE) ====
def count_turrets_near(tile_pos, turret_group, radius_tiles=2):
    count = 0
    # Konversi koordinat tile ke pusat pixel
    px = (tile_pos[0] + 0.5) * c.TILE_SIZE
    py = (tile_pos[1] + 0.5) * c.TILE_SIZE

    for turret in turret_group:
        tx, ty = turret.rect.center
        dist = math.dist((px, py), (tx, ty))
        # Cek jika jarak turret lebih kecil dari radius
        if dist < radius_tiles * c.TILE_SIZE:
            count += 1
    return count

# ==== Hitung total skor jalur berdasarkan jumlah turret di sepanjangnya ====
def evaluate_path(tile_points, turret_group):
    total_score = 0
    for p in tile_points:
        # Skor ditambah berdasarkan jumlah turret dekat waypoint
        total_score += count_turrets_near(p, turret_group)
    return total_score

# ==== Pilih path terbaik (Shortest/Longest) TANPA A* ====
def choose_best_path(json_data, turret_group):
    paths = {}

    # Iterasi hanya pada dua nama path yang sudah ditentukan
    for path_name in ["Shortest", "Longest"]:
        # 1. Temukan layer object group
        obj_layer = next((layer for layer in json_data["layers"]
                          if layer["name"] == path_name and layer["type"] == "objectgroup"), None)

        if not obj_layer:
            print(f"Peringatan: Layer path '{path_name}' tidak ditemukan di JSON.")
            continue # Lanjut ke path berikutnya jika tidak ada

        # 2. Asumsi hanya ada 1 polyline per layer path
        obj = obj_layer["objects"][0]
        poly = obj["polyline"]
        offset_x = obj["x"]
        offset_y = obj["y"]

        pixel_points = []
        tile_points = []

        for p in poly:
            # 3. Ambil koordinat PIXEL (untuk musuh)
            px = p["x"] + offset_x
            py = p["y"] + offset_y
            pixel_points.append((px, py))

            # 4. Konversi ke koordinat TILE (untuk scoring)
            tile_x = int(px // c.TILE_SIZE)
            tile_y = int(py // c.TILE_SIZE)

            # Hindari duplikasi tile yang sama berturut-turut
            if not tile_points or (tile_x, tile_y) != tile_points[-1]:
                tile_points.append((tile_x, tile_y))

        # 5. Hitung skor keamanan path berdasarkan TILE
        score = evaluate_path(tile_points, turret_group)

        # 6. Simpan hasil (simpan PIXEL path)
        paths[path_name] = {
            "path": pixel_points,
            "score": score
        }

    if not paths:
        return [], "None" # Safety check jika kedua path tidak ada

    # 7. Pilih path dengan skor terendah (paling aman)
    best_name = min(paths.keys(), key=lambda n: paths[n]["score"])

    # 8. Kembalikan PIXEL path dan nama path
    return paths[best_name]["path"], best_name