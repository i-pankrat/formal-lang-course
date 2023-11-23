from typing import Set
from collections.abc import Callable

from project.graphs_lib import LABEL
from project.cfg import cfg_to_wcnf

from networkx import Graph
from pyformlang.cfg import CFG, Variable
from scipy.sparse import lil_matrix


def cfpq_request(
    graph: Graph,
    request: CFG,
    algorithm: Callable[Graph, CFG, Set],
    start_vertices: Set = None,
    final_vertices: Set = None,
    start_variable: Variable = Variable("S"),
) -> Set:
    """It allows you to solve a reachability problem for start and final vertices of your graph.
    A reachability constraint is a context-free grammar.

    Parameters
    ----------
    graph : Graph
        Input graph from networkx
    request : CFG
        context-free grammar
    start_vertices: Set
        Start vertices of input graph
    final_vertices: Set
        Final vertices of input graph
    start_variable: Variable
        Start variable to grammar

    Returns
    -------
    res : Set
        Set of pairs of graph vertices that satisfies the request
    """

    if start_vertices is None:
        start_vertices = graph.nodes
    if final_vertices is None:
        final_vertices = graph.nodes

    transitive_closure = algorithm(graph, request)

    res = {
        (start_node, final_node)
        for start_node, variable, final_node in transitive_closure
        if start_node in start_vertices
        and variable == start_variable
        and final_node in final_vertices
    }

    return res


def _prepare_wcfg_for_algorithm(wcnf: CFG) -> (set, set, set):

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

    return epsilon_prods, term_prods, var_prods


def constrained_transitive_closure(graph: Graph, cfg: CFG) -> Set:
    """Find transitive closure of the graph with constraints of cfg grammar

    Parameters
    ----------
    graph : Graph
        Input graph from networkx
    cfg : CFG
        Context-Free Grammar represents constraints

    Returns
    -------
    res : Set
        Constrained transitive closure of graph
    """

    wcnf = cfg_to_wcnf(cfg)
    epsilon_prods, term_prods, var_prods = _prepare_wcfg_for_algorithm(wcnf)

    res = {(node, var.value, node) for node in graph.nodes for var in epsilon_prods} | {
        (first_node, prod.head.value, second_node)
        for first_node, second_node, label in graph.edges.data(LABEL)
        for prod in term_prods
        if prod.body[0].value == label
    }

    queue = res.copy()

    while queue:
        start1, var1, end1 = queue.pop()
        tmp = set()

        for start2, var2, end2 in res:
            if start1 == end2:
                triplets = {
                    (start2, prod.head.value, end1)
                    for prod in var_prods
                    if prod.body[0].value == var2
                    and prod.body[1].value == var1
                    and (start2, prod.head.value, end1) not in res
                }
                queue |= triplets
                tmp |= triplets

            if start2 == end1:
                triplets = {
                    (start1, prod.head.value, end2)
                    for prod in var_prods
                    if prod.body[0].value == var1
                    and prod.body[1].value == var2
                    and (start1, prod.head.value, end2) not in res
                }
                queue |= triplets
                tmp |= triplets

        res |= tmp

    return res


def matrix_closure(graph: Graph, cfg: CFG) -> Set:

    wcnf = cfg_to_wcnf(cfg)
    epsilon_prods, term_prods, var_prods = _prepare_wcfg_for_algorithm(wcnf)

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
