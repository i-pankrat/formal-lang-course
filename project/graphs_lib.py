from typing import Tuple

import cfpq_data
import networkx as nx
import pydot

LABEL = "label"


def get_graph_info(graph_name: str) -> (int, int, set):
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
