import filecmp

import pytest
import cfpq_data
import os
import networkx as nx
import pydot

from project import graphs_lib


def test_get_graph_info_skos():
    # https://formallanguageconstrainedpathquerying.github.io/CFPQ_Data/graphs/data/skos.html#skos

    skos_nodes, skos_edges = 144, 252
    skos_labels = {
        "type",
        "label",
        "definition",
        "isDefinedBy",
        "subPropertyOf",
        "comment",
        "scopeNote",
        "inverseOf",
        "range",
        "domain",
        "contributor",
        "disjointWith",
        "creator",
        "example",
        "first",
        "rest",
        "seeAlso",
        "title",
        "description",
        "unionOf",
        "subClassOf",
    }
    nodes, edges, label_set = graphs_lib.get_graph_info("skos")

    assert skos_nodes == nodes
    assert skos_edges == edges
    assert skos_labels == label_set


def test_get_graph_info_ws():
    # https://formallanguageconstrainedpathquerying.github.io/CFPQ_Data/graphs/data/kernel.html#kernel

    wc_nodes, wc_edges = 332, 269
    wc_labels = {"a", "d"}
    nodes, edges, label_set = graphs_lib.get_graph_info("wc")

    assert wc_nodes == nodes
    assert wc_edges == edges
    assert wc_labels == label_set


def test_labeled_two_cycles_graph_to_dot():
    file_name = "graph"
    full_file_name = file_name + ".dot"
    expected_file_name = "expected_graph"
    full_expected_file_name = expected_file_name + ".dot"
    first_cycle_len = 10
    second_cycle_len = 20
    labels = ("a", "d")

    # Create expecting graph
    cfpq_graph = cfpq_data.labeled_two_cycles_graph(
        first_cycle_len, second_cycle_len, labels=labels
    )

    graphs_lib.write_to_dot(cfpq_graph, expected_file_name)

    # Create a test graph
    graphs_lib.labeled_two_cycles_graph_to_dot(
        file_name, first_cycle_len, second_cycle_len, labels
    )

    assert filecmp.cmp(full_file_name, full_expected_file_name)

    os.remove(full_file_name)
    os.remove(full_expected_file_name)
