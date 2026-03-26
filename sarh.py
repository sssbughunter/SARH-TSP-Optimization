"""
SARH — Structure-Aware Relocation Heuristic for Euclidean TSP
Author: Prakhar Dwivedi, RJIT Gwalior
Paper: "Breaking Local Optima in Euclidean TSP: A Structure-Aware Relocation Heuristic (SARH)"

Key insight: Standard Greedy+2opt gets trapped in local minima because
2-opt only swaps edges — it cannot transport a node to a distant position.
SARH detects structurally misaligned nodes (central nodes visited too late
or creating backtracking) and relocates them before 2-opt runs.
"""

import math
import random
import time

# ── 1. DISTANCE MODULE ────────────────────────────────────────

def euclidean(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def build_dist_matrix(nodes):
    n = len(nodes)
    D = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            d = euclidean(nodes[i], nodes[j])
            D[i][j] = D[j][i] = d
    return D

def tour_length(tour, D):
    n = len(tour)
    return sum(D[tour[i]][tour[(i+1)%n]] for i in range(n))

# ── 2. GREEDY NEAREST NEIGHBOR ────────────────────────────────

def greedy_nn(D, start=0):
    n = len(D)
    unvisited = set(range(n))
    tour = [start]
    unvisited.remove(start)
    while unvisited:
        curr = tour[-1]
        nearest = min(unvisited, key=lambda x: D[curr][x])
        tour.append(nearest)
        unvisited.remove(nearest)
    return tour

# ── 3. 2-OPT LOCAL SEARCH ─────────────────────────────────────

def two_opt(tour, D):
    """Fast 2-opt using delta evaluation."""
    n = len(tour)
    best = list(tour)
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if j == n - 1 and i == 0:
                    continue
                a, b = best[i], best[(i+1)%n]
                c, d = best[j], best[(j+1)%n]
                delta = (D[a][c] + D[b][d]) - (D[a][b] + D[c][d])
                if delta < -1e-10:
                    best[i+1:j+1] = best[i+1:j+1][::-1]
                    improved = True
    return best

# ── 4. GEOMETRIC ANALYZER ─────────────────────────────────────

def centroid(nodes):
    n = len(nodes)
    return (sum(x for x,y in nodes)/n, sum(y for x,y in nodes)/n)

def turning_angle(p_prev, p_curr, p_next):
    v1 = (p_curr[0]-p_prev[0], p_curr[1]-p_prev[1])
    v2 = (p_next[0]-p_curr[0], p_next[1]-p_curr[1])
    m1 = math.sqrt(v1[0]**2+v1[1]**2)
    m2 = math.sqrt(v2[0]**2+v2[1]**2)
    if m1 < 1e-10 or m2 < 1e-10:
        return 180.0
    cos_t = max(-1.0, min(1.0, (v1[0]*v2[0]+v1[1]*v2[1])/(m1*m2)))
    return math.degrees(math.acos(cos_t))

def find_misaligned(tour, nodes, D, angle_threshold=120.0, centroid_ratio=0.7):
    """
    Detects nodes that are structurally misaligned:
    - Creates a sharp turning angle (< angle_threshold)  
    - Is closer to centroid than its neighbors (visited too late)
    
    Uses looser thresholds than paper's strict case to work on general instances.
    Also detects high insertion-cost savings — nodes whose removal+reinsertion 
    gives significant improvement.
    """
    cx, cy = centroid(nodes)
    n = len(tour)
    misaligned = []

    for i in range(n):
        p_prev = nodes[tour[(i-1)%n]]
        p_curr = nodes[tour[i]]
        p_next = nodes[tour[(i+1)%n]]

        angle = turning_angle(p_prev, p_curr, p_next)
        d_curr  = euclidean(p_curr, (cx,cy))
        d_prev  = euclidean(p_prev, (cx,cy))
        d_next  = euclidean(p_next, (cx,cy))
        avg_nbr = (d_prev + d_next) / 2

        # Condition 1: sharp angle + closer to centroid than neighbors
        if angle < angle_threshold and avg_nbr > 0 and (d_curr / avg_nbr) < centroid_ratio:
            misaligned.append(i)
            continue

        # Condition 2: node creates high detour cost — check if relocating saves distance
        # removal_saving = edges removed - edge bridging the gap
        a = tour[(i-1)%n]; b = tour[i]; c = tour[(i+1)%n]
        removal_saving = D[a][b] + D[b][c] - D[a][c]

        # best insertion cost elsewhere
        best_insert = float('inf')
        for j in range(n):
            if j == (i-1)%n or j == i or j == (i+1)%n:
                continue
            p = tour[j]; q = tour[(j+1)%n]
            insert_cost = D[p][b] + D[b][q] - D[p][q]
            if insert_cost < best_insert:
                best_insert = insert_cost

        net_gain = removal_saving - best_insert
        # Only flag if gain is meaningful relative to tour scale
        avg_edge = tour_length(tour, D) / n
        if net_gain > 0.15 * avg_edge:
            misaligned.append(i)

    # Remove duplicates, keep only most impactful (top 20% per iteration)
    seen = set()
    unique = [i for i in misaligned if not (i in seen or seen.add(i))]
    return unique[:max(1, len(unique)//3)]  # conservative — relocate in batches

# ── 5. RELOCATION ENGINE ──────────────────────────────────────

def relocate(tour, nodes, D, misaligned_positions):
    """
    Removes misaligned nodes and reinserts each at its globally optimal position.
    Surgery: splice out → find best insertion → stitch back in.
    """
    working = list(tour)
    # Sort descending so removal doesn't shift earlier indices
    for pos in sorted(set(misaligned_positions), reverse=True):
        node = working.pop(pos)
        # Find best insertion position
        best_cost = float('inf')
        best_pos  = 0
        m = len(working)
        for j in range(m):
            a = working[j]; b = working[(j+1)%m]
            delta = D[a][node] + D[node][b] - D[a][b]
            if delta < best_cost:
                best_cost = delta
                best_pos  = j + 1
        working.insert(best_pos, node)
    return working

# ── 6. SARH MAIN PIPELINE ─────────────────────────────────────

def sarh(nodes, angle_threshold=120.0, centroid_ratio=0.7, max_reloc_rounds=10, verbose=True):
    """
    SARH Full Pipeline:
    Phase 1 — Greedy Nearest Neighbor construction
    Phase 2 — Structural correction: detect misaligned nodes, relocate them
    Phase 3 — 2-opt local refinement on corrected tour
    
    Works on any N. Scales to 1000+ nodes.
    """
    D = build_dist_matrix(nodes)
    n = len(nodes)

    # ── Phase 1: Greedy ──
    t0 = time.perf_counter()
    greedy_tour = greedy_nn(D)
    greedy_len  = tour_length(greedy_tour, D)
    t_greedy = (time.perf_counter()-t0)*1000

    # ── Baseline: Greedy + 2-opt ──
    t0 = time.perf_counter()
    g2opt_tour = two_opt(list(greedy_tour), D)
    g2opt_len  = tour_length(g2opt_tour, D)
    t_g2opt = (time.perf_counter()-t0)*1000

    # ── Phase 2: Structural Correction ──
    t0 = time.perf_counter()
    corrected = list(greedy_tour)
    total_relocated = 0
    prev_len = greedy_len

    for round_num in range(max_reloc_rounds):
        misaligned = find_misaligned(corrected, nodes, D, angle_threshold, centroid_ratio)
        if not misaligned:
            break
        corrected = relocate(corrected, nodes, D, misaligned)
        new_len = tour_length(corrected, D)
        total_relocated += len(misaligned)
        if abs(prev_len - new_len) < 1e-10:
            break
        prev_len = new_len

    # ── Phase 3: 2-opt on corrected tour ──
    sarh_tour = two_opt(corrected, D)
    sarh_len  = tour_length(sarh_tour, D)
    t_sarh = (time.perf_counter()-t0)*1000

    improvement = ((g2opt_len - sarh_len) / g2opt_len * 100) if g2opt_len > 0 else 0

    if verbose:
        print(f"\n{'═'*58}")
        print(f"  SARH  |  N={n}  |  Relocated: {total_relocated} nodes")
        print(f"{'─'*58}")
        print(f"  Greedy (NN)        : {greedy_len:>10.4f}   ({t_greedy:.2f}ms)")
        print(f"  Greedy + 2-opt     : {g2opt_len:>10.4f}   ({t_g2opt:.2f}ms)")
        print(f"  SARH (proposed)    : {sarh_len:>10.4f}   ({t_sarh:.2f}ms)")
        print(f"  Improvement vs 2opt: {improvement:>+.2f}%")
        print(f"{'═'*58}")

    return {
        "nodes": nodes, "D": D,
        "greedy_tour": greedy_tour, "greedy_len": greedy_len,
        "g2opt_tour": g2opt_tour,   "g2opt_len":  g2opt_len,
        "sarh_tour":  sarh_tour,    "sarh_len":   sarh_len,
        "improvement": improvement,  "relocated":  total_relocated,
    }

# ── 7. BENCHMARK ──────────────────────────────────────────────

def benchmark(sizes=[10,25,50,100,200,500], trials=5):
    print(f"\n{'═'*70}")
    print(f"  SARH BENCHMARK")
    print(f"{'─'*70}")
    print(f"  {'N':>5}  {'Greedy':>9}  {'Grdy+2opt':>9}  {'SARH':>9}  {'Improv':>7}  {'Time':>7}")
    print(f"  {'─'*5}  {'─'*9}  {'─'*9}  {'─'*9}  {'─'*7}  {'─'*7}")
    for n in sizes:
        g_l,g2_l,s_l,ts=[],[],[],[]
        for _ in range(trials):
            nodes=[(random.uniform(0,100),random.uniform(0,100)) for _ in range(n)]
            t0=time.perf_counter()
            r=sarh(nodes,verbose=False)
            ts.append((time.perf_counter()-t0)*1000)
            g_l.append(r["greedy_len"]); g2_l.append(r["g2opt_len"]); s_l.append(r["sarh_len"])
        ag=sum(g_l)/trials; ag2=sum(g2_l)/trials; as_=sum(s_l)/trials; at=sum(ts)/trials
        imp=(ag2-as_)/ag2*100 if ag2>0 else 0
        print(f"  {n:>5}  {ag:>9.2f}  {ag2:>9.2f}  {as_:>9.2f}  {imp:>+6.2f}%  {at:>6.1f}ms")
    print(f"{'═'*70}")

# ── MAIN ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  SARH — Structure-Aware Relocation Heuristic for TSP     ║")
    print("║  Author: Prakhar Dwivedi  |  RJIT Gwalior                ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Paper's 9-node test
    print("\n>>> Paper's 9-node instance")
    paper_nodes = [(0,0),(1,4),(3,6),(6,7),(9,6),(11,4),(9,2),(6,1),(3,2),(5,4)]
    sarh(paper_nodes)

    # Random instances
    for n, seed in [(50,42),(100,7),(500,13)]:
        print(f"\n>>> Random {n} nodes")
        random.seed(seed)
        sarh([(random.uniform(0,100),random.uniform(0,100)) for _ in range(n)])

    # Full benchmark
    benchmark([10,25,50,100,200,500])
