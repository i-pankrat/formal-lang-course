import pathlib

from project import automaton_lib as autolib
from project.Automaton import Automaton

from typing import Tuple, List, Set, Optional

import cfpq_data
import networkx as nx
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import State

LABEL = "label"


def get_graph_by_name(graph_name: str) -> nx.MultiDiGraph:
    """Get graph by its graph.

    Parameters
    ----------
    graph_name : str
        The name to the graph from cfpq_data dataset.

    Returns
    -------
    graph : networkx.MultiDiGraph:
        The graph from cfpq_data dataset.
    """
    p = cfpq_data.download(graph_name)
    return cfpq_data.graph_from_csv(p)


def get_graph_info(graph_name: str) -> Tuple[int, int, set]:
    """Get general information about the graph.

    Parameters
    ----------
    graph_name : str
        The name to the graph from cfpq_data dataset.

    Returns
    -------
    nodes, edges, labels : (int, int, set)
        Number of graph's nodes, number of graph's edges
        and labels of the graph.
    """

    g = get_graph_by_name(graph_name)

    # It is assumed that in the whole course the information on the edges is called "label"
    return (
        g.number_of_nodes(),
        g.number_of_edges(),
        set([label for _, _, _, label in g.edges(data=LABEL, keys=True)]),
    )


def labeled_two_cycles_graph_to_dot(
    file_name: str | pathlib.Path,
    first_cycle_len: int,
    second_cycle_len: int,
    labels: Tuple[str, str],
) -> None:
    """Create a graph with two cycles connected by one node
    with labeled edges and save it to dot file.

    Parameters
    ----------
    file_name : str | Path
        The name to the file where the graph will be written.
    first_cycle_len: int
        The length of the first cycle
    second_cycle_len: int
        The length of the second cycle
    labels: Tuple[str, str]
        Labels for the first cycle edges and for the second ones
    """

    graph = cfpq_data.labeled_two_cycles_graph(
        first_cycle_len, second_cycle_len, labels=labels
    )
    write_to_dot(graph, file_name)
    return


def write_to_dot(graph: any, path: str | pathlib.Path):
    """Write graph to .dot file.

    Parameters
    ----------
    graph : any
        The graph from a NetworkX that will be written to the file
    path: str | pathlib.Path
        The name to the file where the graph will be written.
    """

    nx.nx_pydot.to_pydot(graph).write(path)
    return


def make_regex_request_to_graph(
    regex: Regex,
    graph: any,
    start_vertexes: List[any],
    final_vertexes: List[any],
) -> List[Tuple[any, any]]:

    """Perform regular queries on graphs

    Parameters
    ----------
    regex : Regex
        Finite automaton from pyformlang
    graph: nx.MultiDiGraph
        Graph from networkx
    start_vertexes : any
        Start states of finite automaton
    final_vertexes: Optional[List[State]]
        Final states of finite automaton


    Returns
    -------
    fa : any
        Return those pairs of vertices from the given start and end vertices,
        which are connected by a path forming by the regex.
    """

    map(State, start_vertexes)
    map(State, final_vertexes)
    # Convert graph to automaton
    graph_fa = autolib.graph_to_nfa(graph, start_vertexes, final_vertexes)

    # Convert regex to automaton
    regex_fa = autolib.regex_to_minimal_dfa(regex)

    # Convert fa from nx to Automaton
    first_automaton = Automaton.from_fa(graph_fa)
    second_automaton = Automaton.from_fa(regex_fa)
    intersection_automaton = first_automaton.intersect(second_automaton)
    transitive_closure = intersection_automaton.transitive_closure()

    result = []  # List of pairs
    # Add pairs to list
    regex_states_num = len(regex_fa.states)
    new_states_to_graph_states = {
        k: v for v, k in first_automaton.old_state_to_new.items()
    }
    for start in intersection_automaton.start_states:
        for final in intersection_automaton.final_states:
            if transitive_closure[start, final]:
                g_start = new_states_to_graph_states[start // regex_states_num]
                g_final = new_states_to_graph_states[final // regex_states_num]
                result.append((g_start, g_final))

    return result


def bfs_rpq(
    regex: Regex,
    graph: any,
    start_vertexes: Optional[List[any]],
    final_vertexes: Optional[List[any]],
    is_separately: bool,
) -> Set[any]:
    """It allows you to solve a reachability problem on a graph represented as an adjacency matrix and a regular
    expression represented as an adjacency matrix. If the flag is set to true, it solves the reachability
    problem for each individual start vertex, otherwise for the whole set of start vertices.

    Parameters
    ----------
    regex : Automaton
        Regular expression represented as an adjacency matrix
    graph : any
        Graph from networkx
    start_vertexes : Optional[List[any]]
        Start vertexes. If none than all graph nodes are start vertexes
    final_vertexes : Optional[List[any]]
        Final vertexes. If none than all graph nodes are final vertexes
    is_separately : bool
        Flag represented type of solving problem

    Returns
    -------
    States : States : Union[Set[any], Set[Tuple[any, any]]]
        Depending on the type of problem being solved, it returns either a set of reachable states or a set of
        pairs of states, where the first element is responsible for the starting state and the second for the
        ending state.
    """
    if not start_vertexes:
        start_vertexes = graph.nodes
    if not final_vertexes:
        final_vertexes = graph.nodes

    map(State, start_vertexes)
    map(State, final_vertexes)
    # Convert graph to automaton
    graph_fa = autolib.graph_to_nfa(graph, start_vertexes, final_vertexes)

    # Convert regex to automaton
    regex_fa = autolib.regex_to_minimal_dfa(regex)

    # Convert fa from nx to Automaton
    graph_automaton = Automaton.from_fa(graph_fa)
    regex_automaton = Automaton.from_fa(regex_fa)

    result = graph_automaton.bfs_rpq(regex_automaton, is_separately)
    mapping = {v: k for k, v in graph_automaton.old_state_to_new.items()}

    if is_separately:
        map(lambda a, b: (mapping[a], mapping[b]), result)
        return result
    else:
        return {mapping[i] for i in result}


def read_from_dot(file_path: str | pathlib.Path) -> nx.MultiDiGraph:
    """Read graph for .dot file

    Parameters
    ----------
    file_path: str | pathlib.Path
        Path to file.

    Returns
    -------
    graph : nx.MultiDiGraph
        Return read graph from dot file.
    """
    res: nx.MultiDiGraph = nx.drawing.nx_pydot.read_dot(file_path)
    if "\\n" in res.nodes:
        res.remove_node("\\n")

    return res
