# pathfinder.py
import math
import constants as c

# ==== Hitung ancaman turret di posisi pixel tertentu ====
def calculate_threat_at_position(pixel_pos, turret_group):
    """
    Menghitung tingkat ancaman di posisi pixel tertentu.
    Threat dihitung berdasarkan:
    1. Jumlah turret yang bisa hit posisi ini
    2. Jarak ke turret (semakin dekat = semakin berbahaya)
    """
    threat = 0
    px, py = pixel_pos
    
    for turret in turret_group:
        tx, ty = turret.rect.center
        dist = math.sqrt((px - tx)**2 + (py - ty)**2)
        
        # Cek apakah enemy berada dalam range turret
        if dist < turret.range:
            # Semakin dekat = semakin lama kena damage (eksponensial)
            time_in_range = (turret.range - dist) / turret.range
            turret_damage = getattr(turret, 'damage', 1)
            
            # Formula baru: Base + eksponensial penalty
            threat += (10.0 + (time_in_range ** 2) * 20.0) * turret_damage
    
    return threat


# ==== Hitung total ancaman sepanjang path dengan sampling ====
def calculate_path_threat_detailed(pixel_points, turret_group, sample_interval=10):
    """
    Menghitung total ancaman sepanjang path dengan melakukan sampling
    di setiap interval pixel (bukan hanya di waypoint).
    
    Args:
        pixel_points: List koordinat pixel path
        turret_group: Group turret
        sample_interval: Interval sampling (pixels). Makin kecil = lebih akurat tapi lambat
    
    Returns:
        total_threat: Total ancaman sepanjang path
    """
    total_threat = 0
    
    # Iterasi setiap segment path (antara 2 waypoint)
    for i in range(len(pixel_points) - 1):
        p1 = pixel_points[i]
        p2 = pixel_points[i + 1]
        
        # Hitung panjang segment
        segment_length = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        # Tentukan berapa banyak sample points di segment ini
        num_samples = max(int(segment_length / sample_interval), 1)
        
        # Sample threat di sepanjang segment
        for j in range(num_samples + 1):
            t = j / num_samples  # Parameter interpolasi (0 to 1)
            
            # Interpolasi posisi
            sample_x = p1[0] + t * (p2[0] - p1[0])
            sample_y = p1[1] + t * (p2[1] - p1[1])
            
            # Hitung threat di posisi ini
            threat = calculate_threat_at_position((sample_x, sample_y), turret_group)
            total_threat += threat
    
    return total_threat


# ==== Hitung jarak euclidean antar titik ====
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


# ==== Hitung total panjang path ====
def calculate_path_length(pixel_points):
    """
    Menghitung panjang total path.
    """
    total_length = 0
    for i in range(len(pixel_points) - 1):
        total_length += euclidean_distance(pixel_points[i], pixel_points[i + 1])
    return total_length


# ==== Parse path dari JSON ====
def parse_path_from_json(json_data, path_name):
    """
    Ekstrak pixel_points dari JSON untuk path tertentu.
    """
    obj_layer = next((layer for layer in json_data["layers"]
                      if layer["name"] == path_name and layer["type"] == "objectgroup"), None)
    
    if not obj_layer or not obj_layer["objects"]:
        return None
    
    obj = obj_layer["objects"][0]
    poly = obj["polyline"]
    offset_x = obj["x"]
    offset_y = obj["y"]
    
    pixel_points = []
    
    for p in poly:
        px = p["x"] + offset_x
        py = p["y"] + offset_y
        pixel_points.append((px, py))
    
    return pixel_points


# ==== A* Algorithm untuk memilih path terbaik ====
def astar_choose_best_path(json_data, turret_group, sample_interval=1):
    """
    Menggunakan A* algorithm untuk memilih antara Shortest dan Longest path.
    
    Prioritas:
    1. THREAT (tingkat ancaman) - pilih yang paling aman
    2. DISTANCE (jarak) - jika threat hampir sama, pilih yang terpendek
    
    Args:
        json_data: Data map JSON
        turret_group: Group turret yang ada di map
        sample_interval: Interval sampling untuk threat calculation (pixels)
                        Nilai lebih kecil = lebih akurat tapi lebih lambat
                        Default 15 pixels (sekitar 1/3 tile)
    """
    
    # 1. Parse kedua path dari JSON
    paths_data = {}
    for path_name in ["Shortest", "Longest"]:
        pixel_points = parse_path_from_json(json_data, path_name)
        if pixel_points:
            paths_data[path_name] = pixel_points
    
    if not paths_data:
        print("Error: Tidak ada path yang valid ditemukan!")
        return [], "None"
    
    # 2. Jika hanya ada satu path, langsung return
    if len(paths_data) == 1:
        path_name = list(paths_data.keys())[0]
        return paths_data[path_name], path_name
    
    # 3. Evaluasi kedua path dengan A*
    path_evaluations = {}
    
    for path_name, pixel_points in paths_data.items():
        # Hitung distance (G-cost)
        distance = calculate_path_length(pixel_points)
        
        # Hitung threat dengan sampling detail
        threat = calculate_path_threat_detailed(pixel_points, turret_group, sample_interval)
        
        # Normalisasi threat berdasarkan panjang path
        # Ini penting agar path panjang tidak otomatis punya threat lebih tinggi
       # Normalisasi threat berdasarkan panjang path
        if distance > 0:
            # GANTI DARI 1000 KE 50000 UNTUK MEMPERBESAR PERBEDAAN NUMERIK
            normalized_threat = threat / distance * 200000 
        else:
            normalized_threat = 99999999.0
        
        # Normalisasi PER DISTANCE (lebih fair)
        # threat_per_distance = threat / distance if distance > 0 else 0

        path_evaluations[path_name] = {
            "distance": distance,
            "threat": threat,
            "normalized_threat": normalized_threat,
            "pixel_points": pixel_points
        }
        
        # Debug info
        print(f"Path '{path_name}':")
        print(f"  - Distance: {distance:.2f} pixels")
        print(f"  - Raw Threat: {threat:.2f}")
        print(f"  - Normalized Threat: {normalized_threat:.2f}")
    
    # 4. Pilih path berdasarkan prioritas: THREAT > DISTANCE
    threat_values = {name: data["normalized_threat"] for name, data in path_evaluations.items()}
    min_threat = min(threat_values.values())
    max_threat = max(threat_values.values())
    
    # Threshold untuk menentukan apakah threat "hampir sama"
    THREAT_THRESHOLD_PERCENT = 0.25
    threat_difference = max_threat - min_threat
    threat_threshold = max(min_threat * THREAT_THRESHOLD_PERCENT, 100.0)  # Minimal 2.0
    
    if threat_difference > threat_threshold:
        # Threat berbeda signifikan -> pilih yang paling aman (threat terendah)
        best_path_name = min(path_evaluations.keys(), 
                           key=lambda name: path_evaluations[name]["normalized_threat"])
        decision = "Threat berbeda signifikan! Pilih path paling aman"
    else:
        # Threat hampir sama -> pilih yang paling pendek (distance terendah)
        best_path_name = min(path_evaluations.keys(), 
                           key=lambda name: path_evaluations[name]["distance"])
        decision = "Threat hampir sama. Pilih path terpendek"
    
    best_path_data = path_evaluations[best_path_name]
    
    print(f"\n=> {decision}")
    print(f"=> Enemy memilih path: {best_path_name}")
    print(f"   (Normalized Threat: {best_path_data['normalized_threat']:.2f}, "
          f"Distance: {best_path_data['distance']:.2f})\n")
    
    return best_path_data["pixel_points"], best_path_name


# ==== Wrapper function untuk backward compatibility ====
def choose_best_path(json_data, turret_group):
    """
    Fungsi wrapper untuk mempertahankan interface yang sama.
    Sekarang menggunakan A* algorithm dengan threat calculation yang lebih akurat.
    """
    return astar_choose_best_path(json_data, turret_group)