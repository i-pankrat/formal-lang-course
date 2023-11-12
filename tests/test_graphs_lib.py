import filecmp
import os

from project import graphs_lib
from tests.test_utils.manage_path import generate_right_path_to_test_file as gen_path

import networkx as nx
from pyformlang.regular_expression import Regex


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
    file_name = gen_path("graph.dot")
    expected_file_name = gen_path("expected_graph.dot")
    first_cycle_len = 4
    second_cycle_len = 5
    labels = ("a", "d")

    # Create a test graph
    graphs_lib.labeled_two_cycles_graph_to_dot(
        file_name, first_cycle_len, second_cycle_len, labels
    )

    assert filecmp.cmp(file_name, expected_file_name, shallow=False)
    os.remove(file_name)


def test_make_regex_request_to_graph():

    # First test case
    regex = Regex("a.(b|c)*")
    g = nx.MultiDiGraph()
    nodes = [0, 1]
    edges = [
        (nodes[0], nodes[0], {graphs_lib.LABEL: "a"}),
        (nodes[0], nodes[1], {graphs_lib.LABEL: "b"}),
        (nodes[1], nodes[0], {graphs_lib.LABEL: "b"}),
        (nodes[1], nodes[1], {graphs_lib.LABEL: "c"}),
    ]
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    result = [(0, 1)]

    answer = graphs_lib.make_regex_request_to_graph(regex, g, nodes[:1], nodes[1:2])
    assert result == answer

    # Second test case
    g = nx.MultiDiGraph()  # Accepts (a*)|(b*)
    nodes = ["fst", "snd", "thd"]
    edges = [
        (nodes[0], nodes[1], {graphs_lib.LABEL: "a"}),
        (nodes[1], nodes[1], {graphs_lib.LABEL: "a"}),
        (nodes[0], nodes[2], {graphs_lib.LABEL: "b"}),
        (nodes[2], nodes[2], {graphs_lib.LABEL: "b"}),
    ]
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)

    # Regex accepts a*
    regex = Regex("a*")
    result = [("fst", "snd")]
    answer = graphs_lib.make_regex_request_to_graph(regex, g, nodes[:1], nodes[1:2])
    assert result == answer

    # Regex accepts b*
    regex = Regex("b*")
    result = [("fst", "thd")]
    answer = graphs_lib.make_regex_request_to_graph(regex, g, nodes[:1], nodes[2:3])
    assert result == answer


def test_bfs_rpq_for_vertex_set():

    # Test case from
    # https://github.com/FormalLanguageConstrainedPathQuerying/FormalLanguageConstrainedReachability-LectureNotes
    regex = Regex("b*.a.b")
    g = nx.MultiDiGraph()
    nodes = [0, 1, 2, 3]
    edges = [
        (nodes[0], nodes[1], {graphs_lib.LABEL: "a"}),
        (nodes[0], nodes[3], {graphs_lib.LABEL: "b"}),
        (nodes[3], nodes[0], {graphs_lib.LABEL: "b"}),
        (nodes[1], nodes[2], {graphs_lib.LABEL: "b"}),
        (nodes[2], nodes[0], {graphs_lib.LABEL: "a"}),
    ]
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)

    res = graphs_lib.bfs_rpq(regex, g, [nodes[0]], [nodes[2]], False)
    assert res == {nodes[2]}
    # Check case that in case when we have the only one start vertex flag is_separately change nothing
    res = graphs_lib.bfs_rpq(regex, g, [nodes[0]], [nodes[2]], True)
    assert res == {(nodes[0], nodes[2])}
    # Some other tests on the same regex and graph
    res = graphs_lib.bfs_rpq(regex, g, [nodes[3]], nodes, False)
    assert res == {nodes[2]}
    res = graphs_lib.bfs_rpq(regex, g, [nodes[3]], None, False)
    assert res == {nodes[2]}
    res = graphs_lib.bfs_rpq(regex, g, [nodes[2]], nodes, False)
    assert res == {nodes[3]}
    res = graphs_lib.bfs_rpq(regex, g, [nodes[2]], None, False)
    assert res == {nodes[3]}


def test_bfs_rpq_for_every_vertex():
    regex = Regex("a.((c*)|(d*))")
    g = nx.MultiDiGraph()
    nodes = [0, 1, 2, 3]
    edges = [
        (nodes[0], nodes[1], {graphs_lib.LABEL: "a"}),
        (nodes[1], nodes[2], {graphs_lib.LABEL: "a"}),
        (nodes[2], nodes[2], {graphs_lib.LABEL: "d"}),
        (nodes[1], nodes[1], {graphs_lib.LABEL: "c"}),
    ]
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)

    res = graphs_lib.bfs_rpq(regex, g, [nodes[0], nodes[1]], [nodes[1], nodes[2]], True)
    assert res == {(nodes[0], nodes[1]), (nodes[1], nodes[2])}
    # Expect empty set
    res = graphs_lib.bfs_rpq(regex, g, [nodes[2]], None, True)
    assert res == set()
    # Some other tests for the same graph and regex expression
    res = graphs_lib.bfs_rpq(regex, g, None, None, True)
    assert res == {(nodes[0], nodes[1]), (nodes[1], nodes[2])}

    # Change regex expression and do some more tests
    regex = Regex("a.(c*).(a*).(d*)")
    res = graphs_lib.bfs_rpq(regex, g, None, None, True)
    assert res == {(nodes[0], nodes[1]), (nodes[0], nodes[2]), (nodes[1], nodes[2])}

    regex = Regex("a.(c*).a.(d*)")
    res = graphs_lib.bfs_rpq(regex, g, None, None, True)
    assert res == {(nodes[0], nodes[2])}

    regex = Regex("a.(c*)")
    res = graphs_lib.bfs_rpq(regex, g, None, None, True)
    assert res == {(nodes[0], nodes[1]), (nodes[1], nodes[2])}

    regex = Regex("(a*).(c*).(d*)")
    res = graphs_lib.bfs_rpq(regex, g, None, None, True)
    assert res == {
        (nodes[0], nodes[1]),
        (nodes[0], nodes[2]),
        (nodes[1], nodes[2]),
        (nodes[0], nodes[0]),
        (nodes[1], nodes[1]),
        (nodes[2], nodes[2]),
        (nodes[3], nodes[3]),
    }
