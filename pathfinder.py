# pathfinder.py
import math
import constants as c

# ==== Fungsi bantu ====
def is_in_turret_range(pixel_pos, turret):
    """Cek apakah titik pixel berada dalam jangkauan turret."""
    px, py = pixel_pos
    tx, ty = turret.rect.center
    dist = math.sqrt((px - tx) ** 2 + (py - ty) ** 2)
    return dist < turret.range


def calculate_turrets_on_path(pixel_points, turret_group, sample_interval=10):
    """
    Hitung berapa turret yang bisa menjangkau path.
    Jika satu turret bisa menjangkau bagian mana pun dari path, dihitung sekali.
    """
    turrets_in_range = set()

    for turret in turret_group:
        for i in range(len(pixel_points) - 1):
            p1 = pixel_points[i]
            p2 = pixel_points[i + 1]

            segment_length = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
            num_samples = max(int(segment_length / sample_interval), 1)

            for j in range(num_samples + 1):
                t = j / num_samples
                sample_x = p1[0] + t * (p2[0] - p1[0])
                sample_y = p1[1] + t * (p2[1] - p1[1])

                if is_in_turret_range((sample_x, sample_y), turret):
                    turrets_in_range.add(turret)
                    break  # cukup hitung turret ini sekali saja

    return len(turrets_in_range)


def euclidean_distance(p1, p2):
    """Hitung jarak Euclidean antar titik."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def calculate_path_length(pixel_points):
    """Hitung total panjang path."""
    total = 0
    for i in range(len(pixel_points) - 1):
        total += euclidean_distance(pixel_points[i], pixel_points[i + 1])
    return total


def parse_path_from_json(json_data, path_name):
    """Ambil path dari file map JSON."""
    obj_layer = next(
        (
            layer
            for layer in json_data["layers"]
            if layer["name"] == path_name and layer["type"] == "objectgroup"
        ),
        None,
    )

    if not obj_layer or not obj_layer["objects"]:
        return None

    obj = obj_layer["objects"][0]
    poly = obj["polyline"]
    offset_x = obj["x"]
    offset_y = obj["y"]

    return [(p["x"] + offset_x, p["y"] + offset_y) for p in poly]


# ==== A* Algorithm versi baru ====
def astar_choose_best_path(json_data, turret_group, sample_interval=10):
    """
    Algoritma A* versi disederhanakan untuk memilih path terbaik.
    
    Prioritas:
    1. Jumlah turret yang bisa menjangkau path (lebih sedikit lebih baik)
    2. Kalau sama → pilih path terpendek
    """
    # 1. Parse path dari JSON
    paths_data = {}
    for path_name in ["Shortest", "Longest"]:
        pixel_points = parse_path_from_json(json_data, path_name)
        if pixel_points:
            paths_data[path_name] = pixel_points

    if not paths_data:
        print("❌ Tidak ada path valid ditemukan!")
        return [], "None"

    if len(paths_data) == 1:
        name = list(paths_data.keys())[0]
        return paths_data[name], name

    # 2. Evaluasi tiap path (anggap seperti "node" dalam A*)
    path_evaluations = {}
    for path_name, pixel_points in paths_data.items():
        turret_count = calculate_turrets_on_path(pixel_points, turret_group, sample_interval)
        distance = calculate_path_length(pixel_points)

        # Di A*, f = g + h → di sini "f" = bobot total (turret_count + panjang path)
        # Kita tetap jaga format, walaupun path cuma dua
        f_cost = turret_count * 1000 + distance / 1000.0  # Turret jauh lebih berpengaruh

        path_evaluations[path_name] = {
            "turret_count": turret_count,
            "distance": distance,
            "f_cost": f_cost,
            "pixel_points": pixel_points,
        }

        print(f"Path '{path_name}':")
        print(f"  - Jumlah Turret: {turret_count}")
        print(f"  - Panjang Path : {distance:.2f}")
        print(f"  - F-cost (A* heuristic): {f_cost:.2f}")

    # 3. Pilih path dengan f_cost terendah
    best_path_name = min(path_evaluations, key=lambda name: path_evaluations[name]["f_cost"])
    best_path_data = path_evaluations[best_path_name]

    # 4. Logging hasil keputusan
    print("\n=== A* Path Decision ===")
    print(f"=> Enemy memilih path: {best_path_name}")
    print(
        f"   (Turret: {best_path_data['turret_count']}, "
        f"Distance: {best_path_data['distance']:.2f}, "
        f"F-cost: {best_path_data['f_cost']:.2f})\n"
    )

    return best_path_data["pixel_points"], best_path_name


# ==== Wrapper agar tetap kompatibel dengan main.py ====
def choose_best_path(json_data, turret_group):
    """
    Wrapper agar tetap kompatibel dengan kode lama.
    Sekarang memakai A* versi baru dengan prioritas turret_count & distance.
    """
    return astar_choose_best_path(json_data, turret_group)
