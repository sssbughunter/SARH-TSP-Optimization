# SARH — Structure-Aware Relocation Heuristic for Euclidean TSP

> Breaking local optima that Greedy+2-opt cannot escape — through geometric structural analysis and node relocation.

**Author:** Prakhar Dwivedi  
**Institution:** Rustamji Institute of Technology (RJIT), Gwalior  
**Paper:** *"Breaking Local Optima in Euclidean TSP: A Structure-Aware Relocation Heuristic (SARH)"*

---

## The Problem

Standard Greedy Nearest-Neighbor + 2-opt gets permanently stuck in local minima on geometric TSP instances. Here's why:

- **Greedy** visits central nodes too late — forced to backtrack across the entire cluster
- **2-opt** can only swap edges — it **cannot transport a node** to a distant position
- Once stuck, no single edge swap can escape the structural trap

## The Solution: SARH

SARH adds a **structural pre-processing phase** between Greedy and 2-opt:

```
Phase 1: Greedy Nearest-Neighbor construction
Phase 2: Geometric analysis → detect misaligned nodes → relocate them
Phase 3: Standard 2-opt local refinement
```

**Key insight:** Geometry matters. Nodes with sharp turning angles that sit near the centroid are "visited too late" — relocating them before 2-opt runs resolves structural defects that pure edge-swapping cannot fix.

## Results

| Method | Tour Length | vs Greedy |
|--------|-------------|-----------|
| Greedy (NN) | 31.69 | baseline |
| Greedy + 2-opt | 31.69 | 0.00% (stagnated) |
| **SARH (proposed)** | **30.10** | **-5.02%** |

On the paper's 9-node structured instance, SARH achieves a 5.02% improvement while Greedy+2-opt stagnates completely.

## How It Works

### Phase 2 — Geometric Analyzer (the novel part)

For each node in the tour, SARH computes:

1. **Turning angle θ** — the angle formed at the node between incoming and outgoing edges
2. **Centroid proximity ratio** — how close the node is to the centroid vs its neighbors

A node is flagged as **misaligned** if:
- `θ < threshold` (creates a sharp spike in the path)
- Node is significantly closer to centroid than its neighbors (visited too late)

Or if removing and reinserting the node elsewhere yields a significant net gain.

### Phase 2 — Relocation Engine

For each misaligned node:
1. Remove it from the tour
2. Test every possible reinsertion position
3. Permanently insert at the position minimizing `Δcost = d(prev,node) + d(node,next) - d(prev,next)`

This is the "surgery" that 2-opt cannot perform.

## Quick Start

```bash
git clone https://github.com/sssbughunter/SARH-TSP.git
cd SARH-TSP
python3 sarh.py
```

**Requirements:** Python 3.9+ (standard library only — zero dependencies)

## Usage

```python
from sarh import sarh

# Any list of (x, y) coordinates
nodes = [(x1,y1), (x2,y2), ...]

result = sarh(nodes)
# result contains:
# - greedy_tour, greedy_len
# - g2opt_tour, g2opt_len
# - sarh_tour, sarh_len
# - improvement (%)
# - relocated (count)
```

## When SARH Shines

SARH is most effective on **structured geometric instances** where:
- Nodes form clusters with central trap nodes
- Nodes arranged in a ring/circle with interior nodes
- Any layout where greedy ordering creates long backtracking detours

On purely random uniform distributions, the improvement is smaller (0–2%) because structural traps are less common. This is expected and consistent with the paper's claims.

## Repository Structure

```
SARH-TSP/
├── sarh.py          # Complete Python implementation
├── index.html       # Interactive web demo
└── README.md        # This file
```

## Live Demo

🌐 [Interactive Demo](https://sssbughunter.github.io/SARH-TSP/) — visualize all three tours side by side, test on different distributions, run benchmark

## Citation

```
Prakhar Dwivedi, "Breaking Local Optima in Euclidean TSP: A Structure-Aware 
Relocation Heuristic (SARH)," Rustamji Institute of Technology, Gwalior, 2025.
```

---

*SARH — Geometry-aware pre-processing for TSP local search*
