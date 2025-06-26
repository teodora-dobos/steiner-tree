import sys
import networkx as nx
from algorithms.primal_dual import primal_dual
from algorithms.repetitive_shortest_path import repetitive_shortest_path
from algorithms.mehlhorn_algorithm import mehlhorn_algorithm
from algorithms.naive_heuristic import naive_heuristic


def create_graph_from_input():
    """
    Reads a graph in PACE format from stdin.
    """
    # Skip to SECTION Graph
    while True:
        line = sys.stdin.readline()
        if line.startswith("SECTION Graph"):
            break

    num_nodes = int(sys.stdin.readline().split()[1])
    num_edges = int(sys.stdin.readline().split()[1])

    graph = nx.Graph()
    graph.add_nodes_from(range(1, num_nodes + 1))

    for _ in range(num_edges):
        _, u, v, w = sys.stdin.readline().split()
        u, v, w = int(u), int(v), int(w)
        graph.add_edge(u, v, weight=w, similarity=1 / w)

    # Skip until SECTION Terminals
    while True:
        line = sys.stdin.readline()
        if line.startswith("SECTION Terminals"):
            break

    num_terminals = int(sys.stdin.readline().split()[1])
    terminals = []

    for _ in range(num_terminals):
        _, node_id = sys.stdin.readline().split()
        node_id = int(node_id)
        graph.nodes[node_id]['terminal'] = True
        terminals.append(node_id)

    return graph, terminals


def valid_solution(tree, terminals):
    """
    Validates if the solution is a tree, connected, and covers all terminals.
    """
    connected = nx.is_connected(tree)
    if not connected:
        print("❌ Graph is not connected")
    is_tree = nx.is_tree(tree)
    if not is_tree:
        print("❌ Graph is not a tree")
    covers_all = all(t in tree.nodes for t in terminals)
    if not covers_all:
        print("❌ Not all terminals are in the tree")
    return connected and is_tree and covers_all


def run_and_evaluate(name, func, graph, terminals):
    print(f"Running {name}...")
    tree, weight = func(graph, terminals)
    print(f"✅ {name} weight: {weight}")
    print(f"✅ Solution valid: {valid_solution(tree, terminals)}\n")
    return tree


def main():
    graph, terminals = create_graph_from_input()

    print("Running NetworkX approximation...")
    tree_nx = nx.algorithms.approximation.steinertree.steiner_tree(graph, terminals)
    weight_nx = tree_nx.size(weight="weight")
    print(f"✅ NetworkX approximation weight: {weight_nx}")
    print(f"✅ Solution valid: {valid_solution(tree_nx, terminals)}\n")

    run_and_evaluate("Repetitive Shortest Path Heuristic", repetitive_shortest_path, graph, terminals)
    run_and_evaluate("Primal-Dual Algorithm", primal_dual, graph, terminals)
    run_and_evaluate("Mehlhorn Algorithm", mehlhorn_algorithm, graph, terminals)
    run_and_evaluate("Naive Heuristic", naive_heuristic, graph, terminals)

if __name__ == "__main__":
    main()
