from typing import Set

from project.cfg import cfg_to_wcnf

from networkx import Graph
from pyformlang.cfg import CFG, Variable, Terminal
from scipy.sparse import lil_matrix


def matrix_request(
    graph: Graph,
    request: CFG,
    start_vertices: Set = None,
    final_vertices: Set = None,
    start_variable: Variable = Variable("S"),
) -> Set:

    if start_vertices is None:
        start_vertices = graph.nodes
    if final_vertices is None:
        final_vertices = graph.nodes

    transitive_closure = matrix_closure(graph, request)

    res = {
        (start_node, final_node)
        for start_node, variable, final_node in transitive_closure
        if start_node in start_vertices
        and variable == start_variable
        and final_node in final_vertices
    }

    return res


def matrix_closure(graph: Graph, cfg: CFG) -> Set:

    wcnf = cfg_to_wcnf(cfg)
    epsilon_prods = set()
    term_prods = set()
    var_prods = set()

    for prod in wcnf.productions:
        prod_body_len = len(prod.body)

        if prod_body_len == 0:
            epsilon_prods.add(prod.head)
        elif prod_body_len == 1:
            term_prods.add(prod)
        else:  # prod_body_len == 2
            var_prods.add(prod)

    nodes = list(graph.nodes)
    indexes_nodes = {node: i for i, node in enumerate(nodes)}
    n = graph.number_of_nodes()

    matrices = {var: lil_matrix((n, n), dtype=bool) for var in wcnf.variables}

    for i in range(n):
        for var in epsilon_prods:
            matrices[var][i, i] = True

    for u, v, label in graph.edges(data="label"):
        i, j = indexes_nodes[u], indexes_nodes[v]
        for var in term_prods:
            matrices[var.head][i, j] |= label == var.body[0].value

    while True:
        old_nnz = sum([v.nnz for v in matrices.values()])
        for prod in var_prods:
            matrices[prod.head] += matrices[prod.body[0]] @ matrices[prod.body[1]]
        if old_nnz == sum([value.nnz for value in matrices.values()]):
            break

    return set(
        (nodes[i], v, nodes[j])
        for v, mat in matrices.items()
        for i, j in zip(*mat.nonzero())
    )
