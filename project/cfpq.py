from typing import Set
from collections.abc import Callable

from project.cfpq_algorithms import (
    constrained_transitive_closure,
    matrix_closure,
    tensor_closure,
)

from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable


def _cfpq(
    graph: MultiDiGraph,
    request: CFG,
    algorithm: Callable[[MultiDiGraph, CFG], Set],
    start_vertices: Set = None,
    final_vertices: Set = None,
    start_variable: Variable = Variable("S"),
) -> Set:
    """It allows you to solve a reachability problem for start and final vertices of your graph.
    A reachability constraint is a context-free grammar. You may specify algorithm for solving problem.

    Parameters
    ----------
    graph : MultiDiGraph
        Input graph from networkx
    request : CFG
        context-free grammar
    algorithm: Callable[[Graph, CFG], Set]
        Algorithm for cfpq
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


def hellings(
    graph: MultiDiGraph,
    request: CFG,
    start_vertices: Set = None,
    final_vertices: Set = None,
    start_variable: Variable = Variable("S"),
) -> Set:
    """It allows you to solve a reachability problem for start and final vertices of your graph.
    A reachability constraint is a context-free grammar. Hellings algorithm is used for solution.

    Parameters
    ----------
    graph : MultiDiGraph
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
    return _cfpq(
        graph,
        request,
        constrained_transitive_closure,
        start_vertices,
        final_vertices,
        start_variable,
    )


def matrix(
    graph: MultiDiGraph,
    request: CFG,
    start_vertices: Set = None,
    final_vertices: Set = None,
    start_variable: Variable = Variable("S"),
) -> Set:
    """It allows you to solve a reachability problem for start and final vertices of your graph.
    A reachability constraint is a context-free grammar. Matrix algorithm is used for solution.

    Parameters
    ----------
    graph : MultiDiGraph
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
    return _cfpq(
        graph, request, matrix_closure, start_vertices, final_vertices, start_variable
    )


def tensor(
    graph: MultiDiGraph,
    request: CFG,
    start_vertices: Set = None,
    final_vertices: Set = None,
    start_variable: Variable = Variable("S"),
) -> Set:
    """It allows you to solve a reachability problem for start and final vertices of your graph.
    A reachability constraint is a context-free grammar. Tensor algorithm is used for solution.

    Parameters
    ----------
    graph : MultiDiGraph
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
    return _cfpq(
        graph, request, tensor_closure, start_vertices, final_vertices, start_variable
    )
