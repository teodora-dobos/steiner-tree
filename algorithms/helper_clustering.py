import math
import numpy as np
import networkx as nx
import scipy.sparse as sp
from sklearn.cluster import KMeans
from sklearn_extra.cluster import KMedoids


def get_first_eigenvectors(graph):
    """
    Returns the eigenvectors of the Laplacian matrix (sorted by eigenvalue).
    """
    L_sparse = nx.linalg.laplacianmatrix.laplacian_matrix(graph, weight='similarity')
    L_dense = L_sparse.todense()
    eigenvalues, eigenvectors = np.linalg.eigh(np.asarray(L_dense))
    sorted_indices = np.argsort(eigenvalues)
    return eigenvectors[:, sorted_indices]


def spectral_clustering(graph, terminals):
    """
    Clusters nodes using spectral embedding and squared distance to terminal embeddings.
    """
    eigenvectors = get_first_eigenvectors(graph)
    embeddings = eigenvectors[:, 1:len(terminals) + 1]

    clusters = {t: [t] for t in terminals}

    for node in graph.nodes:
        if node not in terminals:
            node_embedding = embeddings[node - 1]
            nearest = min(terminals,
                          key=lambda t: np.sum((node_embedding - embeddings[t - 1]) ** 2))
            clusters[nearest].append(node)

    return clusters


def nearest_terminal_clustering(graph, terminals):
    """
    Assigns each node to the cluster of the terminal to which it has the shortest path.
    """
    clusters = {t: [t] for t in terminals}
    shortest_paths = {
        t: nx.single_source_dijkstra(graph, t, weight='weight')[0] for t in terminals
    }

    for node in graph.nodes:
        if node not in terminals:
            nearest = min(terminals, key=lambda t: shortest_paths[t].get(node, math.inf))
            clusters[nearest].append(node)

    return clusters


def kMeans_clustering(graph, terminals):
    """
    Spectral clustering using KMeans initialized at terminal embeddings.
    Note: KMeans does not guarantee terminals in separate clusters.
    """
    eigenvectors = get_first_eigenvectors(graph)
    embeddings = eigenvectors[:, 1:len(terminals) + 1]

    init_centroids = np.array([embeddings[t - 1] for t in terminals])
    kmeans = KMeans(n_clusters=len(terminals), init=init_centroids, n_init=1, max_iter=100)
    labels = kmeans.fit_predict(embeddings)

    return labels


def kMedoids_clustering(graph, terminals):
    """
    Spectral clustering using KMedoids.
    Note: does not force terminals into separate clusters.
    """
    eigenvectors = get_first_eigenvectors(graph)
    embeddings = eigenvectors[:, 1:len(terminals) + 1]

    kmedoids = KMedoids(n_clusters=len(terminals), random_state=0)
    labels = kmedoids.fit_predict(embeddings)

    return labels


def get_clusters_from_labels(graph, labels, terminals):
    """
    Converts clustering labels into terminal-to-node mapping.
    """
    node_list = list(graph.nodes)
    if len(labels) != len(node_list):
        raise ValueError("Label count doesn't match number of nodes in the graph.")

    for i, node in enumerate(node_list):
        graph.nodes[node]['cluster'] = labels[i]

    clusters = {t: [] for t in range(len(terminals))}
    for node, data in graph.nodes(data=True):
        clusters[data['cluster']].append(node)

    return clusters
