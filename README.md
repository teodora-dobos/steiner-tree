# Algorithms for Solving the Steiner Tree Problem

This repository provides a collection of heuristics and approximation algorithms to solve the Steiner Tree Problem. In this problem, we are given an undirected, weighted graph $G = (V, E)$ and a subset of terminal nodes $T \subseteq V$. The objective is to find a minimum-weight tree in $G$ that spans all terminals. 

---

## Implemented Algorithms

### 1. Repetitive Shortest Path Heuristic
Greedily connects the closest uncovered terminal to the current tree using Dijkstra paths. 

### 2. Primal-Dual 2-Approximation
Based on primal-dual schema. Builds dual variables and merges active sets via tight edges. 

### 3. Mehlhorn's Approximation Algorithm
Implements Mehlhorn’s approach using Voronoi regions and minimum spanning trees in transformed graphs. 

### 4. Naive Clustering-Based Heuristic
Clusters nodes based on proximity to terminals and connects randomly chosen representatives. May return an infesible solution.

---

## Clustering Methods

Used primarily for preprocessing in the naive heuristic.

- `nearest_terminal_clustering`: assigns nodes to nearest terminal based on Dijkstra.
- `spectral_clustering`: clusters nodes using eigenvectors of the Laplacian.
- `kMeans_clustering`, `kMedoids_clustering`: use embeddings from the Laplacian and cluster via sklearn.


## How to run
Run on a graph file:
```bash
   python main.py < graphs/graph1.stp
   ```
This will create a ``results.txt`` file with the results computed with the implemented algorithms and with the `networkx` built-in Steiner tree approximation algorithm.
You can replace ``graph1.stp`` with another graph from ``graphs``.

