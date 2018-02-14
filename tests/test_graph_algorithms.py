import math

import networkx

import graph_algorithms


def test_idfs():
    # Negative cycle exists on A->B->C->A, and from A->C, C->A, but not A->C->D or A->B->E->A
    #         A                     F
    #      B     C               G
    #    E  C   D
    from pytest import approx
    graph = networkx.DiGraph()

    def create_biedge(src, dst, forward, backward=None, penalty=0.01):
        if backward is None:
            backward = 1 / forward
        graph.add_edge(src, dst, rate=-math.log(forward * (1 - penalty)))
        graph.add_edge(dst, src, rate=-math.log(backward * (1 + penalty)))

    create_biedge('a', 'b', 2)
    create_biedge('b', 'e', 2)
    create_biedge('b', 'c', 2)
    create_biedge('a', 'c', 4, 1 / 3)
    create_biedge('c', 'd', 5)
    create_biedge('f', 'g', 3)
    three_list = [['a', 'b', 'a'], ['a', 'c', 'a'], ['f', 'g', 'f']]
    four_list = [
        ['a', 'b', 'e', 'b'],
        ['a', 'b', 'c', 'b'],
        ['a', 'b', 'c', 'a'],
        ['a', 'c', 'b', 'a'],
        ['a', 'c', 'b', 'c'],
        ['a', 'c', 'd', 'c']
    ]
    five_list = [['a', 'b', 'c', 'd', 'c'], ['a', 'c', 'b', 'e', 'b']]

    algorithms = graph_algorithms.GraphAlgorithms(graph, ['a', 'f'])
    assert list(algorithms.idfs(0)) == []
    assert list(algorithms.idfs(1)) == []
    assert list(algorithms.idfs(2)) == three_list
    assert list(algorithms.idfs(3)) == three_list + four_list
    assert list(algorithms.idfs(4)) == three_list + four_list + five_list

    assert algorithms.score_cycle(three_list[0]) == approx(1.0001)
    assert algorithms.score_cycle(three_list[1]) == approx(0.7500750075007501)
    assert algorithms.score_cycle(four_list[0]) == approx(1.0001)
    assert algorithms.get_best_cycles(0) == []
    assert algorithms.get_best_cycles(2) == [
        (approx(0.750075), ['a', 'c', 'a']),
        (approx(1.0001), ['a', 'b', 'a']),
        (approx(1.0001), ['f', 'g', 'f'])
    ]
    assert algorithms.get_best_cycles() == [(approx(0.7500750075007501), ['a', 'c', 'a']),
                                            (approx(0.7576515227280305), ['a', 'b', 'c', 'a']),
                                            (approx(0.9901980297039603), ['a', 'c', 'b', 'a']),
                                            (approx(1.000100010001), ['a', 'b', 'a']),
                                            (approx(1.000100010001), ['a', 'b', 'c', 'b']),
                                            (approx(1.000100010001), ['a', 'b', 'c', 'd', 'c']),
                                            (approx(1.000100010001), ['a', 'b', 'e', 'b']),
                                            (approx(1.000100010001), ['a', 'c', 'b', 'c']),
                                            (approx(1.000100010001), ['a', 'c', 'b', 'e', 'b']),
                                            (approx(1.000100010001), ['a', 'c', 'd', 'c']),
                                            (approx(1.0001000100010002), ['f', 'g', 'f'])]
