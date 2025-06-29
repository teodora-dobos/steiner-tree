import sys
import networkx as nx
from algorithms.primal_dual import primal_dual
from algorithms.repetitive_shortest_path import repetitive_shortest_path
from algorithms.mehlhorn_algorithm import mehlhorn_algorithm
from algorithms.naive_heuristic import naive_heuristic

OUTPUT_FILE = "results.txt"


def create_graph_from_input():
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


def valid_solution(tree, terminals, f):
    connected = nx.is_connected(tree)
    if not connected:
        f.write("Graph is not connected\n")
    is_tree = nx.is_tree(tree)
    if not is_tree:
        f.write("Graph is not a tree\n")
    covers_all = all(t in tree.nodes for t in terminals)
    if not covers_all:
        f.write("Not all terminals are in the tree\n")
    return connected and is_tree and covers_all


def run_and_evaluate(name, func, graph, terminals, f):
    print(f"Running {name}...\n")
    tree, weight = func(graph, terminals)
    f.write(f"{name} weight: {weight}\n")
    f.write(f"Solution valid: {valid_solution(tree, terminals, f)}\n\n")
    return tree


def main():
    graph, terminals = create_graph_from_input()

    with open(OUTPUT_FILE, "w") as f:
        print("Running NetworkX approximation...\n")
        tree_nx = nx.algorithms.approximation.steinertree.steiner_tree(graph, terminals)
        weight_nx = tree_nx.size(weight="weight")
        f.write(f"NetworkX approximation weight: {weight_nx}\n")
        f.write(f"Solution valid: {valid_solution(tree_nx, terminals, f)}\n\n")

        run_and_evaluate("Repetitive Shortest Path Heuristic", repetitive_shortest_path, graph, terminals, f)
        run_and_evaluate("Primal-Dual Algorithm", primal_dual, graph, terminals, f)
        run_and_evaluate("Mehlhorn Algorithm", mehlhorn_algorithm, graph, terminals, f)
        run_and_evaluate("Naive Heuristic", naive_heuristic, graph, terminals, f)


if __name__ == "__main__":
    main()
