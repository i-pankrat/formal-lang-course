from project.rsm import RSM
from project.ecfg import ECFG

from typing import Dict

from pyformlang.cfg import Variable
from pyformlang.finite_automaton import EpsilonNFA
from pyformlang.regular_expression import Regex


class TestCase:
    def __init__(self, rsm: "RSM", expected: Dict[Variable, EpsilonNFA]):
        self.rsm = rsm
        self.expected = expected


def test_from_ecfg():
    def assert_prods_are_equal(real_prods, expected_prods):
        for var, real_dfa in real_prods.items():
            assert var in expected_prods
            expected_dfa = expected_prods[var].to_epsilon_nfa().to_deterministic()
            assert real_dfa.is_equivalent_to(expected_dfa)

    filename = "ecfg_from_file1"
    expected_prods = {
        Variable("S"): Regex("(a|(B|(C|D)))"),
        Variable("B"): Regex("(b|(C|D))"),
        Variable("C"): Regex("(c|D)"),
        Variable("D"): Regex("d"),
    }

    ecfg = ECFG.from_file("static/" + filename + ".ecfg")
    rsm = RSM.from_ecfg(ecfg)
    assert rsm.start == Variable("S")
    assert_prods_are_equal(rsm.productions, expected_prods)
