import networkx as nx


def sort_edges(edges, nodes):
    """
    Sort edges based on their growth value.
    Growth = how much dual variables must increase before edge becomes tight.
    """
    for edge, data in edges.items():
        u, v = data['start_node'], data['end_node']
        growth = data['weight'] - (nodes[u]['dual'] + nodes[v]['dual'])
        if nodes[u]['is_active'] and nodes[v]['is_active']:
            growth /= 2
        data['growth'] = growth
    return sorted(edges, key=lambda e: edges[e]['growth'])


def process_tight_edge(tight_edge, edges, nodes, graph, steiner_tree, covered_edges, x_graph, count_active_sets):
    u, v = edges[tight_edge]['start_node'], edges[tight_edge]['end_node']
    growth = edges[tight_edge]['growth']

    # Update dual variables of active nodes
    for node in nodes:
        if nodes[node]['is_active']:
            nodes[node]['dual'] += growth

    # Add incident edges from u and v
    for n in [u, v]:
        for neighbor in graph.neighbors(n):
            if (n, neighbor) not in covered_edges and (neighbor, n) not in covered_edges:
                weight = graph[n][neighbor]['weight']
                growth = weight - (nodes[n]['dual'] + nodes[neighbor]['dual'])
                if nodes[n]['is_active'] and nodes[neighbor]['is_active']:
                    growth /= 2
                edges[(n, neighbor)] = {
                    'start_node': n, 'end_node': neighbor,
                    'weight': weight, 'growth': growth
                }

    covered_edges.add(tight_edge)
    nodes[u]['is_active'] = nodes[v]['is_active'] = True

    as_u, as_v = nodes[u]['active_set'], nodes[v]['active_set']

    # Case 1: same set → do nothing
    if as_u == as_v:
        pass

    # Case 2 & 3: one node non-terminal → join to terminal's active set
    elif not as_u and as_v:
        x_graph.add_edge(u, v, weight=edges[tight_edge]['weight'])
        as_v.add(u)
        for n in as_v:
            nodes[n]['active_set'] = as_v

    elif as_u and not as_v:
        x_graph.add_edge(u, v, weight=edges[tight_edge]['weight'])
        as_u.add(v)
        for n in as_u:
            nodes[n]['active_set'] = as_u

    # Case 4: merge two active sets
    elif as_u and as_v:
        x_graph.add_edge(u, v, weight=edges[tight_edge]['weight'])
        t1 = next(n for n in as_u if nodes[n]['is_terminal'])
        t2 = next(n for n in as_v if nodes[n]['is_terminal'])

        # Add path connecting the two components to the Steiner tree
        path = nx.shortest_path(x_graph, source=t1, target=t2, weight='weight')
        for a, b in zip(path, path[1:]):
            steiner_tree.add_edge(a, b, weight=x_graph[a][b]['weight'])

        # Merge active sets
        merged_set = as_u.union(as_v)
        for n in merged_set:
            nodes[n]['active_set'] = merged_set

        count_active_sets -= 1

    del edges[tight_edge]
    return count_active_sets


def primal_dual(graph, terminals):
    """
    Primal-Dual 2-approximation algorithm for the Steiner Tree problem.
    Based on growing duals and merging active sets.
    """
    nodes = {
        node: {
            'dual': 0,
            'is_terminal': node in terminals,
            'is_active': node in terminals,
            'active_set': {node} if node in terminals else set()
        }
        for node in graph.nodes
    }

    steiner_tree = nx.Graph()
    steiner_tree.add_nodes_from(terminals)

    x_graph = nx.Graph()
    count_active_sets = len(terminals)

    # Initialize incident edge dictionary
    incident_edges = {}
    for t in terminals:
        for neighbor in graph.neighbors(t):
            edge = (t, neighbor)
            weight = graph[t][neighbor]['weight']
            incident_edges[edge] = {
                'start_node': t, 'end_node': neighbor,
                'weight': weight, 'growth': weight
            }

    covered_edges = set()

    while count_active_sets > 1:
        sorted_edges = sort_edges(incident_edges, nodes)
        tight_edge = sorted_edges[0]
        count_active_sets = process_tight_edge(
            tight_edge, incident_edges, nodes, graph,
            steiner_tree, covered_edges, x_graph, count_active_sets
        )

    # Compute weight
    total_weight = sum(data['weight'] for _, _, data in steiner_tree.edges(data=True))
    return steiner_tree, total_weight
