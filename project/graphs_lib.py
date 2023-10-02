from project import automaton_lib as autolib
from project.Automaton import Automaton

from typing import Tuple, List

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
    file_name: str, first_cycle_len: int, second_cycle_len: int, labels: Tuple[str, str]
) -> None:
    """Create a graph with two cycles connected by one node
    with labeled edges and save it to dot file.

    Parameters
    ----------
    file_name : str
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


def write_to_dot(graph: any, path: str):
    """Write graph to .dot file.

    Parameters
    ----------
    graph : any
        The graph from a NetworkX that will be written to the file
    path: str
        The name to the file where the graph will be written.
    """

    nx.nx_pydot.to_pydot(graph).write(path + ".dot")
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
    start_vertexes: List[any],
    final_vertexes: List[any],
    isSeparately: bool,
) -> List[any]:

    map(State, start_vertexes)
    map(State, final_vertexes)
    # Convert graph to automaton
    graph_fa = autolib.graph_to_nfa(graph, start_vertexes, final_vertexes)

    # Convert regex to automaton
    regex_fa = autolib.regex_to_minimal_dfa(regex)

    # Convert fa from nx to Automaton
    graph_automaton = Automaton.from_fa(graph_fa)
    regex_automaton = Automaton.from_fa(regex_fa)

    answer = graph_automaton.bfs_rpq(regex_automaton, isSeparately)
    mapping = {v: k for k, v in graph_automaton.old_state_to_new.items()}
    return [mapping[i] for i in answer]
