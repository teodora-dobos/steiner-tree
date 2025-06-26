import networkx as nx


def mehlhorn_algorithm(graph, terminals):
    """
    Mehlhorn-style approximation algorithm for the Steiner Tree problem.
    Based on: https://people.mpi-inf.mpg.de/~mehlhorn/ftp/SteinerTrees.pdf
    """

    # Step 1: Augment graph with dummy source s0 connected to all terminals
    s0 = max(graph.nodes) + 1
    graph_augmented = graph.copy()
    for t in terminals:
        graph_augmented.add_edge(s0, t, weight=0)

    distances, paths = nx.single_source_dijkstra(graph_augmented, s0)

    # Build Voronoi regions: assign each node to its closest terminal
    closest_terminal = {}
    for node, path in paths.items():
        for n in reversed(path):
            if n in terminals:
                closest_terminal[node] = {
                    'terminal': n,
                    'distance': distances[node],
                    'path': path[path.index(n):]
                }
                break

    # Step 1b: Compute G1' (graph on terminals with shortest inter-terminal paths)
    d1_prime = {}
    G1_prime = nx.Graph()

    for t1 in terminals:
        for t2 in terminals:
            if t2 <= t1:
                continue
            min_cost = None
            best_u, best_v = None, None

            for u, v in graph.edges:
                if s0 in (u, v):
                    continue
                tu, tv = closest_terminal[u]['terminal'], closest_terminal[v]['terminal']
                if tu == tv or {tu, tv} != {t1, t2}:
                    continue

                cost = (
                    closest_terminal[u]['distance'] +
                    graph[u][v]['weight'] +
                    closest_terminal[v]['distance']
                )

                if min_cost is None or cost < min_cost:
                    min_cost = cost
                    best_u, best_v = u, v

            if min_cost is not None:
                d1_prime[(t1, t2)] = {
                    'distance': min_cost,
                    'node_1': best_u,
                    'node_2': best_v
                }
                G1_prime.add_edge(t1, t2, weight=min_cost)

    # Step 2: MST of G1'
    G2 = nx.minimum_spanning_tree(G1_prime, weight='weight', algorithm='prim')

    # Step 3: Expand MST edges into real paths in original graph
    G3 = nx.Graph()
    for t1, t2 in G2.edges:
        if t1 > t2:
            t1, t2 = t2, t1

        entry = d1_prime[(t1, t2)]
        u, v = entry['node_1'], entry['node_2']
        G3.add_edge(u, v, weight=graph[u][v]['weight'])

        for path in [closest_terminal[u]['path'], closest_terminal[v]['path']]:
            for a, b in zip(path, path[1:]):
                G3.add_edge(a, b, weight=graph[a][b]['weight'])

    # Step 4: Compute MST of expanded graph
    G4 = nx.minimum_spanning_tree(G3, weight='weight', algorithm='prim')

    # Step 5: Prune non-terminal leaves
    pruned = True
    while pruned:
        pruned = False
        leaves = [n for n in G4.nodes if G4.degree[n] == 1 and n not in terminals]
        if leaves:
            G4.remove_nodes_from(leaves)
            pruned = True

    total_weight = sum(data['weight'] for _, _, data in G4.edges(data=True))
    return G4, total_weight
