from typing import Set

from project.graphs_lib import LABEL
from project.cfg import cfg_to_wcnf
from project.ecfg import ECFG
from project.automaton_lib import Automaton
from project.rsm import RSM

from networkx import MultiDiGraph
from pyformlang.cfg import CFG
from pyformlang.finite_automaton import EpsilonNFA
from scipy.sparse import lil_matrix, csr_array
from scipy import sparse


def _prepare_wcfg_for_algorithm(wcnf: CFG) -> (Set, Set, Set):
    """Convert wcnf to the set of epsilon productions, the set of terminal production
    and the set of productions where each production body contains of two variables.

    Parameters
    ----------
    wcnf : CFG
        Input graph from networkx

    Returns
    -------
    res : (Set, Set, Set)
        Set of epsilon productions, set of terminal production,
        set of productions where each production body contains of two variables
    """

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


def constrained_transitive_closure(graph: MultiDiGraph, cfg: CFG) -> Set:
    """Find transitive closure of the graph with constraints of cfg grammar
    Use hellings algorithm.

    Parameters
    ----------
    graph : MultiDiGraph
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


def matrix_closure(graph: MultiDiGraph, cfg: CFG) -> Set:
    """Find transitive closure of the graph with constraints of cfg grammar
    Use matrix algorithm.

    Parameters
    ----------
    graph : MultiDiGraph
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

    nodes = list(graph.nodes)
    indexes_nodes = {node: i for i, node in enumerate(nodes)}
    n = graph.number_of_nodes()

    matrices = {var: lil_matrix((n, n), dtype=bool) for var in wcnf.variables}

    for i in range(n):
        for var in epsilon_prods:
            matrices[var][i, i] = True

    for u, v, label in graph.edges(data=LABEL):
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
        for v, matrix in matrices.items()
        for i, j in zip(*matrix.nonzero())
    )


def tensor_closure(graph: MultiDiGraph, cfg: CFG) -> Set:
    """Find transitive closure of the graph with constraints of cfg grammar.
    Use tensor algorithm.

    Parameters
    ----------
    graph : MultiDiGraph
        Input graph from networkx
    cfg : CFG
        Context-Free Grammar represents constraints

    Returns
    -------
    res : Set
        Constrained transitive closure of graph
    """
    ecfg = ECFG.from_cfg(cfg)
    rsm = RSM.from_ecfg(ecfg).minimize()
    rsm_matrix = Automaton.from_rsm(rsm)
    rsm_states = {i: state for state, i in rsm_matrix.old_state_to_new.items()}

    graph_matrix = Automaton.from_fa(EpsilonNFA.from_networkx(graph))
    n = len(graph_matrix.states)
    graph_states = {i: state for state, i in graph_matrix.old_state_to_new.items()}

    id_mat = sparse.eye(n, dtype=bool).todok()
    for var in cfg.get_nullable_symbols():
        if var.value not in graph_matrix.symbol_matrices:
            graph_matrix.symbol_matrices[var.value] = csr_array((n, n), dtype=bool)
            graph_matrix.symbols.add(var.value)
        graph_matrix.symbol_matrices[var.value] += id_mat

    prev_nnz = 0

    while True:
        tc_nnz_indexes = list(
            zip(*rsm_matrix.intersect(graph_matrix).transitive_closure().nonzero())
        )
        if len(tc_nnz_indexes) == prev_nnz:
            break

        prev_nnz = len(tc_nnz_indexes)

        for i, j in tc_nnz_indexes:
            cfg_i, cfg_j = i // n, j // n
            graph_i, graph_j = i % n, j % n

            state_source = rsm_states[cfg_i]
            state_target = rsm_states[cfg_j]

            var, _ = state_source.value

            if (
                state_source in rsm_matrix.start_states
                and state_target in rsm_matrix.final_states
            ):
                if var not in graph_matrix.symbol_matrices:
                    graph_matrix.symbols.add(var)
                    graph_matrix.symbol_matrices[var] = csr_array((n, n), dtype=bool)
                graph_matrix.symbol_matrices[var][graph_i, graph_j] = True

    return {
        (graph_states[graph_i], var, graph_states[graph_j])
        for var, mat in graph_matrix.symbol_matrices.items()
        for graph_i, graph_j in zip(*mat.nonzero())
    }
