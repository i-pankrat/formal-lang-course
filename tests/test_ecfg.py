from project.ecfg import ECFG
from project.cfg import read_grammar_from_file
from project.automaton_lib import regex_to_minimal_dfa

from pyformlang.cfg import Variable, Terminal
from pyformlang.regular_expression import Regex


def test_ecfg_from_cfg():
    test_files = ["balanced_parentheses", "a_or_b"]

    for filename in test_files:
        cfg = read_grammar_from_file("tests/static/" + filename + ".cfg")
        ecfg = ECFG.from_cfg(cfg)
        assert ecfg.start == cfg.start_symbol
        assert len(ecfg.productions) == 1


# This test also check that ecfg_from_text work properly
def test_ecfg_from_file():
    def assert_prod_are_equal(real_prod, expected_prod):
        for var, reg in real_prod.items():
            assert var in expected_prod
            real_dfa = regex_to_minimal_dfa(reg)
            expected_dfa = regex_to_minimal_dfa(expected_prod[var])
            assert real_dfa.is_equivalent_to(expected_dfa)

    filename = "ecfg_from_file1"
    expected_prods = {
        Variable("S"): Regex("(a|(B|(C|D)))"),
        Variable("B"): Regex("(b|(C|D))"),
        Variable("C"): Regex("(c|D)"),
        Variable("D"): Regex("d"),
    }
    expected_vars = {Variable("S"), Variable("D"), Variable("C"), Variable("B")}
    expected_terminals = {Terminal("a"), Terminal("b"), Terminal("c"), Terminal("d")}
    ecfg = ECFG.from_file("tests/static/" + filename + ".ecfg")

    assert ecfg.start == Variable("S")
    assert_prod_are_equal(ecfg.productions, expected_prods)
    assert ecfg.terminals == expected_terminals
    assert ecfg.variables == expected_vars
