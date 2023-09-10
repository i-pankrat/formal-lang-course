from typing import Tuple

import cfpq_data
import networkx as nx

LABEL = "label"


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

    p = cfpq_data.download(graph_name)
    g = cfpq_data.graph_from_csv(p)

    labels_set = set()
    # It is assumed that in the whole course the information on the edges is called "label"
    for _, _, _, label in g.edges(data=LABEL, keys=True):
        labels_set.add(label)

    return g.number_of_nodes(), g.number_of_edges(), labels_set


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
    pydot_graph = nx.nx_pydot.to_pydot(graph)
    pydot_graph.write_dot(file_name + ".dot")
    return
