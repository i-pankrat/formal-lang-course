import random
from string import ascii_lowercase, ascii_uppercase, ascii_letters

import networkx as nx
import pydot
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    State,
    Symbol,
    EpsilonNFA,
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)

from project import automaton_lib, graphs_lib


def test_regex_to_minimal_dfa():
    class RegexTest:
        def __init__(self, regex, test_cases):
            self.regex = regex
            self.tests = test_cases

    test_cases = [
        RegexTest(Regex("$"), [([], True), (["a"], False)]),
        RegexTest(Regex("a"), [(["a"], True), (["a", "a"], False)]),
        RegexTest(
            Regex("a*|b*"),
            [
                (["a", "a"], True),
                (["b", "b"], True),
                (["a", "b", "a"], False),
                (["b", "a", "b"], False),
                (["a", "b", "c"], False),
                (["c", "b"], False),
            ],
        ),
        RegexTest(
            Regex("(a*)|(b*)|(c*)"),
            [
                (["a"], True),
                (["a", "b"], False),
                (["c", "c", "c"], True),
                (["a", "a"], True),
                (["b", "b"], True),
                (["b", "c"], False),
            ],
        ),
        RegexTest(
            Regex("(0|1)*111"),
            [
                (["111"], True),
                (["1", "1", "111"], True),
                (["0", "1", "111"], True),
                (["0", "1", "11"], False),
                (["1", "1", "1"], False),
                (["111", "111"], False),
            ],
        ),
        RegexTest(
            Regex("(0|1)*1.1.1"),
            [
                (["1", "1", "1", "1"], True),
                (["0", "1", "1", "1"], True),
                (["1", "1", "1"], True),
                (["0", "1", "111"], False),
                (["1", "1", "11"], False),
                (["00", "1", "1"], False),
            ],
        ),
        RegexTest(
            Regex("29.(1|2|3|4|5|6|7|8|9|10|11|12).2003"),
            [(["29", str(i), "2003"], True) for i in range(1, 13)]
            + [
                (["30", "1", "2003"], False),
                (["29", "1", "2002"], False),
            ],
        ),
    ]

    for i in range(0, len(test_cases)):
        minimal_dfa = automaton_lib.regex_to_minimal_dfa(test_cases[i].regex)
        for test, result in test_cases[i].tests:
            assert minimal_dfa.accepts(test) == result


def test_graph_to_nfa_from_cpfq_data():

    # https://formallanguageconstrainedpathquerying.github.io/CFPQ_Data/graphs/data/skos.html#skos
    nodes, edges, labels_num = 144, 252, 21
    g = graphs_lib.get_graph_by_name("skos")

    # All states are final and initial
    nfa = automaton_lib.graph_to_nfa(g, None, None)
    assert len(nfa.states) == nodes
    assert len(nfa.start_states) == nodes
    assert len(nfa.final_states) == nodes
    assert len(nfa.symbols) == labels_num

    # Some states are final and initial
    random.seed("formal lang course")
    start_nodes, final_nodes = [], []
    for node in g.nodes():
        random_int = random.randint(1, 100)
        if random_int % 5 == 0:
            start_nodes.append(State(node))

        if random_int % 9 == 0:
            final_nodes.append(State(node))

    nfa = automaton_lib.graph_to_nfa(
        g, start_states=start_nodes, final_states=final_nodes
    )
    assert len(nfa.states) == nodes
    assert len(nfa.start_states) == len(start_nodes)
    assert len(nfa.final_states) == len(final_nodes)
    assert len(nfa.symbols) == labels_num


def test_graph_to_nfa_from_graph():
    g = nx.MultiDiGraph()
    nodes = ["Barnaul", "Saint Petersburg", "Kazan", "Moscow", "Bryansk"]
    edges = [
        (nodes[0], nodes[1], {"label": "4056"}),
        (nodes[1], nodes[2], {"label": "1526"}),
        (nodes[2], nodes[3], {"label": "816"}),
        (nodes[3], nodes[4], {"label": "393"}),
        (nodes[4], nodes[0], {"label": "3994"}),
    ]
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)

    nfa = automaton_lib.graph_to_nfa(g, None, None)
    assert len(nfa.states) == len(nodes)
    assert len(nfa.start_states) == len(nodes)
    assert len(nfa.final_states) == len(nodes)
    assert len(nfa.symbols) == len(edges)

    nfa = automaton_lib.graph_to_nfa(g, [State(nodes[0])], [State(nodes[4])])
    assert len(nfa.states) == len(nodes)
    assert len(nfa.start_states) == 1
    assert len(nfa.final_states) == 1
    assert len(nfa.symbols) == len(edges)


def test_graph_to_nfa_from_dot():
    filename = "tests/static/graph_to_nfa"
    f, s, labels = 2, 3, ("a", "b")
    nodes, labels_num = f + s + 1, 2
    full_filename = "tests/static/graph_to_nfa" + ".dot"
    graphs_lib.labeled_two_cycles_graph_to_dot(filename, f, s, labels=labels)
    pydot_graph = pydot.graph_from_dot_file(full_filename)
    assert len(pydot_graph) == 1
    nx_graph: nx.MultiDiGraph = nx.drawing.nx_pydot.from_pydot(pydot_graph[0])
    nx_graph.remove_node("\\n")

    nfa = automaton_lib.graph_to_nfa(nx_graph, None, None)
    assert len(nfa.states) == nodes
    assert len(nfa.start_states) == nodes
    assert len(nfa.final_states) == nodes
    assert len(nfa.symbols) == labels_num


def test_intersect_two_finite_automatons():
    class TestCase:
        def __init__(self, fa1, fa2, result_fa):
            self.fa1 = fa1
            self.fa2 = fa2
            self.result_fa = result_fa

    symb_a = Symbol("a")
    symb_b = Symbol("b")
    symb_c = Symbol("c")

    # An example from the lecture is used as one case study test
    def first_fa() -> any:
        fa = EpsilonNFA()

        state0 = State(0)
        state1 = State(1)

        fa.add_start_state(state0)
        fa.add_final_state(state1)

        fa.add_transition(state0, symb_a, state0)
        fa.add_transition(state0, symb_b, state1)
        fa.add_transition(state1, symb_b, state0)
        fa.add_transition(state1, symb_c, state1)
        return fa

    def second_fa() -> any:
        fa = EpsilonNFA()

        state0 = State(0)
        state1 = State(1)

        fa.add_start_state(state0)
        fa.add_final_state(state1)

        fa.add_transition(state0, symb_a, state0)
        fa.add_transition(state0, symb_a, state1)
        fa.add_transition(state1, symb_b, state1)
        fa.add_transition(state1, symb_c, state1)
        return fa

    def result_fa() -> any:
        fa = EpsilonNFA()

        state0 = State(0)
        state1 = State(1)
        state3 = State(3)
        fa.add_transitions(
            [
                (state0, symb_a, state0),
                (state0, symb_a, state1),
                (state1, symb_b, state3),
                (state3, symb_c, state3),
                (state3, symb_b, state1),
            ]
        )
        fa.add_start_state(state0)
        fa.add_final_state(state3)
        return fa

    # NFA with digits and ascii letters
    def nfa_accepts_capital_letters() -> any:
        regex_str = "".join(["(", "|".join(ascii_uppercase), ")", "*"])
        return automaton_lib.regex_to_minimal_dfa(Regex(regex_str))

    def nfa_accepts_lowercase_letters() -> any:
        regex_str = "".join(["(", "|".join(ascii_lowercase), ")", "*"])
        return automaton_lib.regex_to_minimal_dfa(Regex(regex_str))

    def nfa_accepts_all_letters() -> any:
        regex_str = "".join(["(", "|".join(ascii_letters), ")", "*"])
        return automaton_lib.regex_to_minimal_dfa(Regex(regex_str))

    def nfa_accepts_digits() -> any:
        regex_str = "".join(["(", "|".join("123456789"), ")", "*"])
        return automaton_lib.regex_to_minimal_dfa(Regex(regex_str))

    def nfa_accepts_digits_and_capital_letters() -> any:
        regex_str = "".join(["(", "|".join(ascii_uppercase + "123456789"), ")", "*"])
        return automaton_lib.regex_to_minimal_dfa(Regex(regex_str))

    def nfa_accepts_digits_and_lowercase_letters() -> any:
        regex_str = "".join(["(", "|".join(ascii_lowercase + "123456789"), ")", "*"])
        return automaton_lib.regex_to_minimal_dfa(Regex(regex_str))

    def empty_fa() -> any:
        state = State(0)
        fa = EpsilonNFA()
        fa.add_start_state(state)
        fa.add_final_state(state)
        return fa

    fa = {
        "empty": empty_fa(),
        "accepts_digits_and_lowercase_letters": nfa_accepts_digits_and_lowercase_letters(),
        "accepts_digits_and_capital_letters": nfa_accepts_digits_and_capital_letters(),
        "accepts_digits": nfa_accepts_digits(),
        "accepts_all_letters": nfa_accepts_all_letters(),
        "accepts_lowercase_letters": nfa_accepts_lowercase_letters(),
        "accepts_capital_letters": nfa_accepts_capital_letters(),
        "first": first_fa(),
        "second": second_fa(),
        "result": result_fa(),
    }

    test_cases = [
        TestCase(fa["first"], fa["second"], fa["result"]),
        TestCase(EpsilonNFA(), fa["result"], EpsilonNFA()),
        TestCase(
            DeterministicFiniteAutomaton(), fa["result"], DeterministicFiniteAutomaton()
        ),
        TestCase(
            NondeterministicFiniteAutomaton(),
            fa["result"],
            NondeterministicFiniteAutomaton(),
        ),
        TestCase(
            fa["accepts_all_letters"],
            fa["accepts_capital_letters"],
            fa["accepts_capital_letters"],
        ),
        TestCase(
            fa["accepts_all_letters"],
            fa["accepts_lowercase_letters"],
            fa["accepts_lowercase_letters"],
        ),
        TestCase(
            fa["accepts_capital_letters"], fa["accepts_lowercase_letters"], fa["empty"]
        ),
        TestCase(
            fa["accepts_digits_and_capital_letters"],
            fa["accepts_digits_and_lowercase_letters"],
            fa["accepts_digits"],
        ),
    ]

    for case in test_cases:
        res = automaton_lib.intersect_two_finite_automatons(case.fa1, case.fa2)
        assert res.is_equivalent_to(case.result_fa)
