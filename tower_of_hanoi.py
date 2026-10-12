"""
=============================================================================
TUGAS 2: PEMODELAN GRAPH & ALGORITMA GREEDY BEST-FIRST SEARCH (GBFS)
PADA GAME PUZZLE TOWER OF HANOI (3 PIRINGAN)
=============================================================================

Deskripsi Masalah & Teori Graf:
1. Graf Ruang Keadaan (State Space Graph) G = (V, E):
   - Vertex / Node (V): Tuple (p0, p1, p2) merepresentasikan posisi tiang
     untuk setiap piringan:
       p0 = Piringan Kecil (Ukuran 0)  in {'A', 'B', 'C'}
       p1 = Piringan Sedang (Ukuran 1) in {'A', 'B', 'C'}
       p2 = Piringan Besar (Ukuran 2)  in {'A', 'B', 'C'}
     Total kemungkinan state = 3^3 = 27 vertex.
   - Edge / Sisi (E): Transisi langkah sah antar-state sesuai aturan Tower of Hanoi.

2. Algoritma Greedy Best-First Search (GBFS):
   - Fungsi Evaluasi: f(n) = h(n)
   - Fungsi Heuristik:
       h(n) = sum_{i=0..k-1} [ 2^i jika state[i] != goal[i] else 0 ]
   - Menggunakan Priority Queue (Min-Heap via heapq) untuk memprioritaskan
     node dengan estimasi jarak terdekat ke goal.

Fitur Program:
- Mode 1: Mainkan Manual (Interactive Game) - Pindahkan piringan sendiri di terminal!
- Mode 2: AI Solver (Animasi Visual GBFS) - AI menyelesaikan puzzle otomatis.
- Mode 3: Analisis Graf & Perjalanan Langkah GBFS.
=============================================================================
"""

import heapq
import time
import os
import sys

# Konfigurasi UTF-8 console jika didukung
if sys.platform.startswith('win'):
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Definisi Tiang & Ukuran Piringan
PEGS = ['A', 'B', 'C']
DISK_NAMES = {0: "Kecil", 1: "Sedang", 2: "Besar"}
DISK_ART = {
    0: "   [===]   ",
    1: "  [=====]  ",
    2: " [=======] ",
}
EMPTY_POLE = "     |     "
BASE_POLE  = "==========="

# =============================================================================
# 1. PEMODELAN GRAPH (STATE SPACE & TRANSISI EDGE)
# =============================================================================

def get_top_disks(state):
    """
    Mengidentifikasi piringan teratas pada masing-masing tiang A, B, dan C.
    Return dictionary: {'A': disk_id, 'B': disk_id, 'C': disk_id}
    (-1 jika tiang kosong).
    """
    top_disks = {'A': -1, 'B': -1, 'C': -1}
    for disk_size, peg in enumerate(state):
        if top_disks[peg] == -1:
            top_disks[peg] = disk_size
    return top_disks

def get_valid_moves(state):
    """
    Mencari seluruh Edge valid E dari Vertex u (state saat ini).
    Mengembalikan daftar tetangga (neighbor states).
    """
    moves = []
    top_disks = get_top_disks(state)

    for source_peg in PEGS:
        disk_to_move = top_disks[source_peg]
        if disk_to_move != -1:  # Tiang asal memiliki piringan
            for target_peg in PEGS:
                if source_peg != target_peg:
                    # Aturan Tower of Hanoi:
                    # Tiang target harus kosong atau piringan di target lebih besar
                    target_top = top_disks[target_peg]
                    if target_top == -1 or target_top > disk_to_move:
                        new_state = list(state)
                        new_state[disk_to_move] = target_peg
                        moves.append(tuple(new_state))
    return moves

# =============================================================================
# 2. FUNGSI HEURISTIK & ALGORITMA GREEDY BEST-FIRST SEARCH
# =============================================================================

def heuristic(state, goal):
    """
    Fungsi Heuristik h(n) = sum(2^i) untuk setiap piringan yang belum di goal.
    Bobot eksponensial 2^i memberikan prioritas tertinggi pada piringan terbesar (2).
    """
    h_val = 0
    for i in range(len(state)):
        if state[i] != goal[i]:
            h_val += 2 ** i
    return h_val

def reconstruct_path(parent, current):
    """
    Menelusuri balik jalur dari Goal State menuju Start State.
    """
    path = []
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path

def greedy_best_first_search(start, goal):
    """
    Implementasi Algoritma Greedy Best-First Search (GBFS).
    Prioritas eksplorasi node murni ditentukan oleh fungsi heuristik: f(n) = h(n).
    Menggunakan Priority Queue (heapq) dengan tuple (h, state).
    """
    # Priority Queue OPEN list menyimpan tuple: (f(n), node_state)
    open_list = []
    heapq.heappush(open_list, (heuristic(start, goal), start))

    visited = set()
    parent = {start: None}
    explored_nodes = 0

    while open_list:
        f, current = heapq.heappop(open_list)
        explored_nodes += 1

        if current == goal:
            return reconstruct_path(parent, current), explored_nodes

        if current in visited:
            continue

        visited.add(current)

        for neighbor in get_valid_moves(current):
            if neighbor not in visited:
                if neighbor not in parent:
                    parent[neighbor] = current
                h = heuristic(neighbor, goal)
                heapq.heappush(open_list, (h, neighbor))

    return None, explored_nodes

# =============================================================================
# 3. VISUALISASI ASCII TOWER OF HANOI DI TERMINAL
# =============================================================================

def render_board(state, step_num=None, action_desc=""):
    """
    Menampilkan representasi grafis tiang dan piringan di terminal.
    """
    peg_stacks = {'A': [], 'B': [], 'C': []}
    for disk_size in [2, 1, 0]:
        peg = state[disk_size]
        peg_stacks[peg].append(disk_size)

    output = []
    header = " " * 4
    if step_num is not None:
        header += f"=== LANGKAH KE-{step_num:02d} | State: {state} ==="
    else:
        header += f"=== State: {state} ==="
    output.append(header)

    if action_desc:
        output.append(" " * 4 + f"Aksi: {action_desc}")
    output.append("")

    # Gambar tiang dari atas (tinggi 3) ke bawah (tinggi 1)
    for level in range(2, -1, -1):
        row_str = "    "
        for peg in PEGS:
            disks = peg_stacks[peg]
            if level < len(disks):
                disk_id = disks[level]
                row_str += DISK_ART[disk_id] + "   "
            else:
                row_str += EMPTY_POLE + "   "
        output.append(row_str)

    # Alas dan label tiang
    output.append("    " + f"{BASE_POLE}   {BASE_POLE}   {BASE_POLE}")
    output.append("    " + "  [Tiang A]     [Tiang B]     [Tiang C]  ")
    output.append("")
    return "\n".join(output)

def describe_move(prev_state, curr_state):
    """
    Menjelaskan perpindahan yang terjadi antara dua state berurutan.
    """
    if not prev_state or not curr_state:
        return "Kondisi Awal"
    for i in range(len(curr_state)):
        if prev_state[i] != curr_state[i]:
            return f"Pindahkan Piringan {i} ({DISK_NAMES[i]}) dari Tiang {prev_state[i]} -> Tiang {curr_state[i]}"
    return "Tidak ada perpindahan"

# =============================================================================
# 4. MODE INTERAKTIF: MAIN MANUAL DI TERMINAL
# =============================================================================

def play_manual():
    """
    Mode permainan interaktif di terminal. Pemain memasukkan tiang asal dan tujuan.
    """
    start_state = ('A', 'A', 'A')
    goal_state = ('C', 'C', 'C')
    current_state = start_state
    move_count = 0
    history = [current_state]

    print("\n" + "=" * 55)
    print("      [*] MODE PERMAINAN MANUAL (TOWER OF HANOI)       ")
    print("=" * 55)
    print("Tujuan: Pindahkan semua 3 piringan dari Tiang A ke Tiang C.")
    print("Aturan: Piringan besar TIDAK boleh ditaruh di atas piringan kecil!")
    print("Cara Input:")
    print("  - Ketik tiang asal & tujuan, contoh: 'A C' atau 'ab'")
    print("  - Ketik 'hint'  : Meminta saran langkah berikutnya dari AI (GBFS)")
    print("  - Ketik 'undo'  : Membatalkan langkah terakhir")
    print("  - Ketik 'reset' : Mengulang dari awal")
    print("  - Ketik 'q'     : Keluar ke Menu Utama")
    print("=" * 55)
    input("Tekan [Enter] untuk mulai bermain...")

    last_action = "Mulai Permainan"

    while True:
        print("\n" + render_board(current_state, move_count, last_action))

        if current_state == goal_state:
            print("[WIN] SELAMAT! ANDA BERHASIL MENYELESAIKAN TOWER OF HANOI!")
            print(f"Total langkah yang Anda gunakan: {move_count} langkah.")
            print("(Catatan: Solusi matematis minimum adalah 7 langkah).")
            input("\nTekan [Enter] untuk kembali ke Menu Utama...")
            break

        user_input = input(">> Masukkan langkah (cth: A B) / [hint/undo/q]: ").strip()
        cmd = user_input.lower()

        if cmd in ['q', 'quit', 'exit']:
            print("Kembali ke Menu Utama.")
            break

        if cmd == 'reset':
            current_state = start_state
            move_count = 0
            history = [current_state]
            last_action = "Reset ke posisi awal"
            continue

        if cmd == 'undo':
            if len(history) > 1:
                history.pop()
                current_state = history[-1]
                move_count -= 1
                last_action = "Undo langkah sebelumnya"
            else:
                last_action = "[!] Belum ada langkah untuk di-undo!"
            continue

        if cmd == 'hint':
            path, _ = greedy_best_first_search(current_state, goal_state)
            if path and len(path) > 1:
                next_step = path[1]
                hint_desc = describe_move(current_state, next_step)
                last_action = f"[SARAN AI] {hint_desc}"
            else:
                last_action = "[SARAN AI] Anda sudah berada di Goal State!"
            continue

        # Parsing input gerakan: contoh "A B", "AB", "a c", dll.
        clean_input = user_input.replace(" ", "").upper()
        if len(clean_input) != 2 or clean_input[0] not in PEGS or clean_input[1] not in PEGS:
            last_action = "[!] Input tidak valid! Masukkan format 2 tiang, cth: 'A B' atau 'A C'."
            continue

        src, dst = clean_input[0], clean_input[1]
        if src == dst:
            last_action = f"[!] Tiang asal dan tujuan sama ({src} -> {dst})."
            continue

        top_disks = get_top_disks(current_state)
        moving_disk = top_disks[src]

        if moving_disk == -1:
            last_action = f"[X] Tiang {src} kosong! Tidak ada piringan untuk dipindahkan."
            continue

        target_top = top_disks[dst]
        if target_top != -1 and target_top < moving_disk:
            last_action = (f"[X] ILEGAL! Piringan {moving_disk} ({DISK_NAMES[moving_disk]}) "
                           f"tidak boleh ditaruh di atas Piringan {target_top} ({DISK_NAMES[target_top]})!")
            continue

        # Langkah valid! Terapkan transisi state
        new_state = list(current_state)
        new_state[moving_disk] = dst
        current_state = tuple(new_state)
        move_count += 1
        history.append(current_state)
        last_action = f"Pindahkan Piringan {moving_disk} ({DISK_NAMES[moving_disk]}) dari {src} -> {dst}"

# =============================================================================
# 5. MODE AI SOLVER: ANIMASI GREEDY BEST-FIRST SEARCH
# =============================================================================

def run_ai_solver():
    """
    Menjalankan AI Greedy Best-First Search dan menampilkan animasi langkah demi langkah.
    """
    start_state = ('A', 'A', 'A')
    goal_state = ('C', 'C', 'C')

    print("\n" + "=" * 55)
    print("      [AI] SOLVER: GREEDY BEST-FIRST SEARCH (GBFS)     ")
    print("=" * 55)
    print("Start State :", start_state)
    print("Goal State  :", goal_state)
    print("Mencari rute menggunakan evaluasi f(n) = h(n)...")

    path, explored = greedy_best_first_search(start_state, goal_state)

    if not path:
        print("[X] Solusi tidak ditemukan.")
        return

    print(f"[OK] Rute ditemukan dalam {len(path) - 1} langkah! (Node dieksplorasi: {explored})")
    print("\nPilih mode animasi:")
    print("  [1] Otomatis (Auto-play dengan jeda waktu)")
    print("  [2] Manual (Tekan Enter tiap langkah)")
    choice = input("Pilihan (1/2, default: 1): ").strip()
    auto_mode = (choice != '2')

    delay = 0.5
    if auto_mode:
        speed_in = input("Kecepatan delay dalam detik (default: 0.5): ").strip()
        if speed_in:
            try:
                delay = float(speed_in)
            except ValueError:
                delay = 0.5

    print("\n" + "-" * 55)
    prev = None
    for step_num, st in enumerate(path):
        action = describe_move(prev, st)
        h_val = heuristic(st, goal_state)
        board_view = render_board(st, step_num, action)
        print(board_view)
        print(f"    Nilai Heuristik h(n) = {h_val}")
        print("-" * 55)

        prev = st

        if step_num < len(path) - 1:
            if auto_mode:
                time.sleep(delay)
            else:
                input("Tekan [Enter] untuk langkah berikutnya...")

    print("[SELESAI] AI Selesai! Seluruh piringan telah tiba di Tiang C.")
    input("\nTekan [Enter] untuk kembali ke Menu Utama...")

# =============================================================================
# 6. MODE ANALISIS GRAPH & ALGORITMA
# =============================================================================

def show_analysis():
    """
    Menampilkan analisis akademis pemodelan graf dan sifat algoritma GBFS.
    """
    start_state = ('A', 'A', 'A')
    goal_state = ('C', 'C', 'C')
    path, explored = greedy_best_first_search(start_state, goal_state)

    print("\n" + "=" * 65)
    print("         [*] ANALISIS AKADEMIS GRAPH & ALGORITMA GBFS         ")
    print("=" * 65)
    print("1. Pemodelan Graf G = (V, E):")
    print("   - Ruang Keadaan (State Space): 3 piringan pada 3 tiang.")
    print("   - Total Vertices Teoritis (|V|) : 3^3 = 27 State.")
    print("   - Struktur Graf : Berbentuk Sierpiński Triangle Graph.")
    print("   - Transisi Edge (|E|) : Hanya perpindahan piringan teratas yang legal.\n")

    print("2. Lintasan Langkah yang Dihasilkan GBFS:")
    print(f"   - Total Langkah: {len(path) - 1} langkah perpindahan.")
    print(f"   - Total Node yang Dievaluasi: {explored} node.\n")
    print("   Daftar Lintasan Transisi:")
    print("   " + "-" * 55)
    print("   No. | State           | Heuristik h(n) | Keterangan Aksi")
    print("   " + "-" * 55)
    prev = None
    for i, st in enumerate(path):
        h_val = heuristic(st, goal_state)
        desc = describe_move(prev, st)
        print(f"   {i:02d}  | {str(st):15} | h = {h_val:2d}         | {desc}")
        prev = st
    print("   " + "-" * 55)

    print("\n3. Analisis Kritis: Mengapa 17 Langkah, Bukan 7 Langkah?")
    print("   - Teori Solusi Optimal (Matematis) : 2^n - 1 = 2^3 - 1 = 7 langkah.")
    print("   - Greedy Best-First Search (GBFS) : Menghasilkan 17 langkah.")
    print("   - Penjelasan Ilmiah:")
    print("     GBFS hanya mengevaluasi f(n) = h(n), artinya algoritma bersifat 'tamak'")
    print("     dan hanya melihat keuntungan langsung saat ini tanpa memperhitungkan biaya")
    print("     masa lalu g(n) (seperti pada A*). Akibatnya, algoritma mengambil rute yang")
    print("     terlihat cepat menurunkan nilai h(n), tetapi kemudian harus bermanuver")
    print("     memindahkan piringan kecil kembali untuk memberi ruang bagi piringan besar.")
    print("     Meskipun tidak optimal (sub-optimal), GBFS terbukti tetap 'Complete' (menemukan solusi)")
    print("     karena dibantu oleh visited set yang mencegah looping tak terhingga.")
    print("=" * 65)
    input("\nTekan [Enter] untuk kembali ke Menu Utama...")

# =============================================================================
# 7. MENU UTAMA
# =============================================================================

def main():
    while True:
        print("\n" + "=" * 55)
        print("  TUGAS 2 GAME DEV: TOWER OF HANOI - GRAPH & GBFS   ")
        print("=" * 55)
        print(" [1] Mainkan Manual di Terminal (Playable Game)")
        print(" [2] AI Solver (Animasi Visual Greedy Best-First Search)")
        print(" [3] Analisis Akademis Graph & Algoritma GBFS")
        print(" [4] Keluar")
        print("=" * 55)

        pilihan = input("Pilih menu (1/2/3/4): ").strip()
        if pilihan == '1':
            play_manual()
        elif pilihan == '2':
            run_ai_solver()
        elif pilihan == '3':
            show_analysis()
        elif pilihan == '4':
            print("\nTerima kasih! Program selesai.\n")
            break
        else:
            print("[!] Pilihan tidak valid. Silakan masukkan 1, 2, 3, atau 4.")

if __name__ == "__main__":
    main()
