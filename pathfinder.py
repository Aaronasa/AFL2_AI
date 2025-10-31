# pathfinder.py
import heapq
import math
import constants as c

# Biaya untuk berjalan di petak berbahaya
DANGER_COST = 10 

class Node:
    """Node untuk algoritma A*"""
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position # (x, y)
        self.g = 0 # Jarak dari awal
        self.h = 0 # Heuristic (jarak ke akhir)
        self.f = 0 # f = g + h

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

    def __hash__(self):
        return hash(self.position)

def heuristic(a, b):
    """Menghitung heuristic (Manhattan distance)"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Fungsi di-update untuk menerima 'danger_zones'
def find_path(tile_map_1d, start_pos_xy, end_pos_xy, turret_tiles, danger_zones):
    """
    Mencari path dari start ke end menggunakan A*.
    Args:
        tile_map_1d: List 1D dari tile map (world.tile_map)
        start_pos_xy: Tuple (x, y) tile start
        end_pos_xy: Tuple (x, y) tile end
        turret_tiles: Set berisi tuple (x, y) dari semua turret (obstacle)
        danger_zones: Set berisi tuple (x, y) dari petak yg ter-cover turret
    """
    
    if not start_pos_xy or not end_pos_xy:
        print("❌ A* Error: Start atau End Pos tidak ditemukan.")
        return None

    # Tile yang boleh dilewati (Jalan, Start, End)
    walkable_tile_ids = {c.PATH_TILE_ID, c.START_TILE_ID, c.END_TILE_ID}

    start_node = Node(None, start_pos_xy)
    end_node = Node(None, end_pos_xy)

    open_list = []
    closed_set = set()

    heapq.heappush(open_list, start_node)

    while open_list:
        try:
            current_node = heapq.heappop(open_list)
        except IndexError:
            break # Open list kosong, tidak ada path

        closed_set.add(current_node.position)

        # Path ditemukan
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Kembalikan path dari Awal -> Akhir

        # Cek tetangga (Atas, Bawah, Kiri, Kanan)
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (
                current_node.position[0] + new_position[0],
                current_node.position[1] + new_position[1]
            )

            # 1. Cek Batasan Map
            if (node_position[0] > (c.COLS - 1) or 
                node_position[0] < 0 or 
                node_position[1] > (c.ROWS - 1) or 
                node_position[1] < 0):
                continue

            # 2. Cek apakah sudah di closed list
            if node_position in closed_set:
                continue

            # 3. Cek apakah obstacle (Turret)
            if node_position in turret_tiles:
                continue

            # 4. Cek apakah tile bisa dilewati (bukan rumput)
            tile_index = node_position[1] * c.COLS + node_position[0]
            tile_id = tile_map_1d[tile_index]
            if tile_id not in walkable_tile_ids:
                continue

            # Jika semua OK, buat node baru
            new_node = Node(current_node, node_position)

            # --- INI LOGIKA BARU ---
            # Hitung biaya bergerak ke petak ini
            move_cost = 1 # Biaya normal
            if node_position in danger_zones:
                move_cost = DANGER_COST # Biaya jika berbahaya!

            new_node.g = current_node.g + move_cost
            # --- AKHIR LOGIKA BARU ---

            new_node.h = heuristic(new_node.position, end_node.position)
            new_node.f = new_node.g + new_node.h

            # Cek jika tetangga sudah di open list
            if any(open_node.position == new_node.position and new_node.g > open_node.g for open_node in open_list):
                continue
                
            heapq.heappush(open_list, new_node)

    print("❌ A* Error: Tidak ada path yang ditemukan.")
    return None # Tidak ada path