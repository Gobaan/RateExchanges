import collections
import math

import networkx


class GraphAlgorithms(object):
    def __init__(self, graph, roots):
        self.graph = graph
        self.roots = roots

    def bellman_ford(self, root):
        distances = collections.defaultdict(lambda: 1000000)
        predecessors = {}
        distances[root] = 0
        for _ in self.graph.nodes:
            for u, v, distance in self.graph.edges(data='rate'):
                if distance + distances[u] < distances[v]:
                    distances[v] = distance + distances[u]
                    predecessors[v] = u

    # Returns all cycles, simple or not
    def idfs(self, k):
        def DLS(node, depth):
            if node in visited and not depth:
                yield [node]
                return
            if node in visited:
                return
            visited.add(node)
            if depth > 0:
                for neighbour in self.graph.adj[node]:
                    for children in DLS(neighbour, depth - 1):
                        yield [node] + children
            visited.remove(node)
            return

        for depth in range(1, k + 1):
            for root in self.roots:
                visited = set()
                for nodes in DLS(root, depth):
                    yield nodes

    def score_cycle(self, cycle):
        attributes = networkx.get_edge_attributes(self.graph, 'rate')
        cycle = cycle[cycle.index(cycle[-1]):]
        return math.exp(sum(attributes[(start, end)] for start, end in zip(cycle, cycle[1:])))

    def get_best_cycles(self, max_depth=5):
        return sorted((self.score_cycle(cycle), cycle) for cycle in self.idfs(max_depth))
