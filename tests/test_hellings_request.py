from project.hellings_request import helling_request
from project.graphs_lib import read_from_dot
from project.cfg import read_grammar_from_file

import pytest


@pytest.mark.parametrize(
    "graph, cfg, start, final, expected",
    [
        (
            read_from_dot("static/graph0.dot"),
            read_grammar_from_file("static/a_or_b.cfg"),
            None,
            None,
            {
                ("1", "1"),
                ("1", "2"),
                ("1", "3"),
                ("1", "5"),
                ("2", "2"),
                ("2", "3"),
                ("2", "5"),
                ("3", "3"),
                ("5", "5"),
            },
        ),
        (
            read_from_dot("static/graph1.dot"),
            read_grammar_from_file("static/a_or_b.cfg"),
            None,
            None,
            {
                ("1", "3"),
                ("6", "6"),
                ("10", "10"),
                ("5", "6"),
                ("2", "3"),
                ("8", "8"),
                ("1", "4"),
                ("1", "5"),
                ("3", "3"),
                ("2", "4"),
                ("11", "11"),
                ("8", "9"),
                ("2", "5"),
                ("1", "1"),
                ("4", "4"),
                ("3", "4"),
                ("5", "5"),
                ("1", "2"),
                ("9", "9"),
                ("1", "6"),
                ("2", "2"),
                ("2", "6"),
                ("7", "7"),
            },
        ),
        (
            read_from_dot("static/empty_graph.dot"),
            read_grammar_from_file("static/empty.cfg"),
            None,
            None,
            set(),
        ),
        (
            read_from_dot("static/empty_graph.dot"),
            read_grammar_from_file("static/balanced_parentheses.cfg"),
            None,
            None,
            set(),
        ),
        (
            read_from_dot("static/graph1.dot"),
            read_grammar_from_file("static/empty.cfg"),
            {"1"},
            {"2", "3", "4", "5", "6", "7", "8", "9"},
            set(),
        ),
        (
            read_from_dot("static/graph2.dot"),
            read_grammar_from_file("static/balanced_parentheses.cfg"),
            {"1"},
            {"2", "3", "4", "5", "6", "7", "8", "9"},
            {("1", "9"), ("1", "5"), ("1", "7"), ("1", "3")},
        ),
        (
            read_from_dot("static/graph3.dot"),
            read_grammar_from_file("static/lang.cfg"),
            {"1"},
            None,
            {("1", "1"), ("1", "4"), ("1", "5"), ("1", "8"), ("1", "10")},
        ),
        (
            read_from_dot("static/arithmetic_graph.dot"),
            read_grammar_from_file("static/arithmetic.cfg"),
            {"1"},
            None,
            {("1", "4"), ("1", "10"), ("1", "2"), ("1", "5"), ("1", "1")},
        ),
        (
            read_from_dot("static/arithmetic_graph.dot"),
            read_grammar_from_file("static/a_or_b.cfg"),
            {"1"},
            None,
            {("1", "1")},
        ),
        (
            read_from_dot("static/arithmetic_graph.dot"),
            read_grammar_from_file("static/lang.cfg"),
            None,
            None,
            set(),
        ),
    ],
)
def test_helling_request(graph, cfg, start, final, expected):
    assert helling_request(graph, cfg, start, final) == expected
