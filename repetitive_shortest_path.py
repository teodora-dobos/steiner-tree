import math
import networkx as nx


def repetitive_shortest_path(graph, terminals):
    """
    Greedy heuristic for Steiner Tree: connects terminals iteratively
    by adding the shortest path to the closest uncovered terminal.
    """
    # Precompute shortest paths from each terminal
    shortest_paths = {
        terminal: {
            'length': nx.single_source_dijkstra(graph, terminal, weight='weight')
        } for terminal in terminals
    }

    # Ensure symmetry of terminal-to-terminal paths
    for t1 in terminals:
        lengths_t1, paths_t1 = shortest_paths[t1]['length']
        for t2 in terminals:
            if t1 < t2:
                _, paths_t2 = shortest_paths[t2]['length']
                paths_t2[t1] = paths_t1[t2]

    steiner_tree = nx.Graph()
    covered = {terminals[0]}
    uncovered = set(terminals[1:])

    while uncovered:
        best_path = None
        best_terminal = None
        min_dist = math.inf

        for t in covered:
            lengths, paths = shortest_paths[t]['length']
            for u in uncovered:
                if lengths.get(u, math.inf) < min_dist:
                    min_dist = lengths[u]
                    best_path = paths[u]
                    best_terminal = u

        # Add best path to tree
        for u, v in zip(best_path, best_path[1:]):
            steiner_tree.add_edge(u, v, weight=graph[u][v]['weight'])

        covered.add(best_terminal)
        uncovered.remove(best_terminal)

    # Prune non-terminal leaf nodes
    pruned = True
    while pruned:
        pruned = False
        for node in list(steiner_tree.nodes):
            if node not in terminals and steiner_tree.degree[node] == 1:
                steiner_tree.remove_node(node)
                pruned = True

    total_weight = sum(data['weight'] for _, _, data in steiner_tree.edges(data=True))
    return steiner_tree, total_weight
