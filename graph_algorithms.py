import collections

import numpy


def bellman_ford(graph, root):
    distances = collections.defaultdict(lambda: 1000000)
    predecessors = {}
    distances[root] = 0
    for i in graph.nodes:
        for u, v, distance in graph.edges(data='rate'):
            if distance + distances[u] < distances[v]:
                distances[v] = distance + distances[u]
                predecessors[v] = u


def floyd_warshall(indices, graph, number_of_iterations=1):
    distances = numpy.full((graph.number_of_nodes(), graph.number_of_nodes()), numpy.inf)
    predecessors = {}
    for src, dst, distance in graph.edges(data='rate'):
        u = indices[src]
        v = indices[dst]
        distances[u][v] = distance

    for k in range(number_of_iterations):
        for src in indices:
            for dst in indices:
                if distance + distances[u] < distances[v]:
                    distances[v] = distance + distances[u]
                    predecessors[v] = u


# gets the best negative simple cycle of size k
def iDFS(graph, roots, k):
    def DLS(node, depth):
        if not depth and node is root:
            return [node]
        if depth > 0:
            for neighbour in graph.adj[node]:
                for children in DLS(neighbour, depth - 1):
                    if children:
                        yield [node] + [children]
        return []

    for i in range(k):
        for root in roots:
            for nodes in DLS(root, i):
                print(nodes)


def testIDFS():
    # Negative cycle exists on A->B->C->A, and from A->C, C->A, but not A->C->D or A->B->E->A
    #         A
    #      B     C
    #    E  C   D
    import networkx
    graph = networkx.DiGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "A")
