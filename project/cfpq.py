from typing import Set
from collections.abc import Callable

from networkx import Graph
from pyformlang.cfg import CFG, Variable

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