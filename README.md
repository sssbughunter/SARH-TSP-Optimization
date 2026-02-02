# SARH: Structure-Aware Relocation Heuristic for TSP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Research](https://img.shields.io/badge/Status-Research-blue.svg)]()

This repository implements the **Structure-Aware Relocation Heuristic (SARH)**, a novel node-relocation strategy designed to optimize convergence in the Traveling Salesman Problem (TSP). 

## 🧠 The Theory
Traditional heuristics like 2-opt often stagnate in local optima due to geometric "crossings" that are locally stable but globally inefficient. SARH prioritizes **structural correction** over simple edge exchanges. By identifying and relocating nodes based on their geometric influence on the global tour, SARH effectively "untangles" the route.

## 📈 Performance Benchmarks
* **Greedy Baseline:** 31.69 tour length.
* **SARH Optimized:** 30.10 tour length.
* **Impact:** Significant reduction in path cost with minimal computational overhead compared to metaheuristics like Simulated Annealing.

## 🛠 Features
* Geometric structural alignment logic.
* Euclidean distance optimization modules.
* Visualization of tour convergence.

---
*Research focused on Structural Alignment and Combinatorial Optimization.*
