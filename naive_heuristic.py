import math
import random
import networkx as nx

from clustering import nearest_terminal_clustering


def naive_heuristic(graph, terminals):
    """
    A naive heuristic using clustering and random representatives.
    There is no guarantee the output is a valid minimal Steiner tree.
    """
    steiner_tree = nx.Graph()

    clusters = nearest_terminal_clustering(graph, terminals)

    # Pick a random representative for each cluster
    representatives = {random.choice(nodes): cluster_id for cluster_id, nodes in clusters.items()}
    rep_list = list(representatives.keys())

    # Precompute shortest paths between representatives
    shortest_paths = {r: [] for r in rep_list}
    for i, r1 in enumerate(rep_list):
        for r2 in rep_list[i + 1:]:
            dist, path = nx.single_source_dijkstra(graph, source=r1, target=r2, weight='weight')
            shortest_paths[r1].append({'cluster': r2, 'distance': dist, 'path': path})
            shortest_paths[r2].append({'cluster': r1, 'distance': dist, 'path': list(reversed(path))})

    # Start from one representative
    covered = [rep_list[0]]
    current = rep_list[0]

    # Connect representative to a node in its cluster
    target_terminal = random.choice(clusters[representatives[current]])
    if current != target_terminal:
        _, path = nx.single_source_dijkstra(graph, current, target_terminal, weight='weight')
        add_path_to_tree(steiner_tree, graph, path)

    # Iteratively connect the next closest uncovered representative
    while len(covered) < len(rep_list):
        best_dist = math.inf
        best_repr = None
        from_repr = None

        for r in covered:
            for entry in shortest_paths[r]:
                if entry['cluster'] not in covered and entry['distance'] < best_dist:
                    best_dist = entry['distance']
                    best_repr = entry['cluster']
                    from_repr = r
                    best_path = entry['path']

        if best_repr is None:
            break  # disconnected

        # Connect the best representative to the current tree
        add_path_to_tree(steiner_tree, graph, best_path)
        covered.append(best_repr)

        # Connect the new representative to its own cluster
        target_terminal = random.choice(clusters[representatives[best_repr]])
        if best_repr != target_terminal:
            _, path = nx.single_source_dijkstra(graph, best_repr, target_terminal, weight='weight')
            add_path_to_tree(steiner_tree, graph, path)

    # Calculate total weight
    total_weight = sum(data['weight'] for _, _, data in steiner_tree.edges(data=True))
    return steiner_tree, total_weight


def add_path_to_tree(tree, graph, path):
    for u, v in zip(path, path[1:]):
        tree.add_edge(u, v, weight=graph[u][v]['weight'])
