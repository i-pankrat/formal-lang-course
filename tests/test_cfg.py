from typing import Iterable
from os.path import join

from project import cfg

from pyformlang.cfg import CFG, Variable, Terminal, Production, Epsilon


def test_cfg_to_wcnf():
    def test_regex():
        var_S = Variable("S")
        ter_a = Terminal("a")

        p0 = Production(var_S, [ter_a, var_S])
        p1 = Production(var_S, [Epsilon()])

        a_cfg = CFG({var_S}, {ter_a}, var_S, {p0, p1})

        # Test a* cfg
        wcnf_cfg = cfg.cfg_to_wcnf(a_cfg)
        assert wcnf_cfg.terminals == a_cfg.terminals
        assert len(wcnf_cfg.productions) == len(a_cfg.productions) + 1
        assert len(wcnf_cfg.variables) == len(a_cfg.variables) + 1
        assert wcnf_cfg.contains([Epsilon()]) == a_cfg.contains([Epsilon()])
        assert wcnf_cfg.contains([ter_a]) == a_cfg.contains([ter_a])
        assert wcnf_cfg.contains([ter_a, ter_a, ter_a, ter_a]) == a_cfg.contains(
            [ter_a, ter_a, ter_a, ter_a]
        )

    def test_an_bn():
        var_S = Variable("S")
        ter_a = Terminal("a")
        ter_b = Terminal("b")

        p0 = Production(var_S, [ter_a, var_S, ter_b])
        p1 = Production(var_S, [ter_a, ter_b])

        an_bn_cfg = CFG({var_S}, {ter_a, ter_b}, var_S, {p0, p1})

        # Test a^nb^n cfg
        wcnf_cfg = cfg.cfg_to_wcnf(an_bn_cfg)
        assert wcnf_cfg.terminals == an_bn_cfg.terminals
        assert len(wcnf_cfg.productions) == len(an_bn_cfg.productions) + 5
        assert len(wcnf_cfg.variables) == len(an_bn_cfg.variables) + 5
        assert wcnf_cfg.contains([Epsilon()]) == an_bn_cfg.contains([Epsilon()])
        assert wcnf_cfg.contains([ter_a, ter_b]) == an_bn_cfg.contains([ter_a, ter_b])
        assert wcnf_cfg.contains([ter_a, ter_a, ter_b, ter_b]) == an_bn_cfg.contains(
            [ter_a, ter_a, ter_b, ter_b]
        )

    def test_removing_chain():
        var_S = Variable("S")
        var_USELESS1 = Variable("USELESS1")
        var_USELESS2 = Variable("USELESS2")
        ter_a = Terminal("a")
        ter_b = Terminal("b")

        p0 = Production(var_S, [var_USELESS1])
        p1 = Production(var_USELESS1, [var_USELESS2])
        p2 = Production(var_USELESS2, [ter_a])
        p3 = Production(var_USELESS2, [ter_b])

        rem_chain_cfg = CFG({var_S}, {ter_a, ter_b}, var_S, {p0, p1, p2, p3})

        # Test removing useless variables
        wcnf_cfg = cfg.cfg_to_wcnf(rem_chain_cfg)
        assert wcnf_cfg.terminals == rem_chain_cfg.terminals
        assert len(wcnf_cfg.productions) == len(rem_chain_cfg.productions) - 2
        assert len(wcnf_cfg.variables) == len(rem_chain_cfg.variables) - 2
        assert wcnf_cfg.contains([ter_a]) == rem_chain_cfg.contains([ter_a])
        assert wcnf_cfg.contains([ter_b]) == rem_chain_cfg.contains([ter_b])

    def test_balanced_parentheses():
        var_S = Variable("S")
        ter_par1 = Terminal("(")
        ter_par2 = Terminal(")")

        p0 = Production(var_S, [Epsilon()])
        p1 = Production(var_S, [var_S, var_S])
        p2 = Production(var_S, [ter_par1, var_S, ter_par2])

        parentheses_cfg = CFG({var_S}, {ter_par1, ter_par2}, var_S, {p0, p1, p2})

        # Test removing useless variables
        wcnf_cfg = cfg.cfg_to_wcnf(parentheses_cfg)
        assert wcnf_cfg.terminals == parentheses_cfg.terminals
        assert len(wcnf_cfg.productions) == len(parentheses_cfg.productions) + 3
        assert len(wcnf_cfg.variables) == len(parentheses_cfg.variables) + 3
        assert wcnf_cfg.contains([ter_par1, ter_par2]) == parentheses_cfg.contains(
            [ter_par1, ter_par2]
        )
        assert wcnf_cfg.contains(
            [ter_par1, ter_par2, ter_par1, ter_par1, ter_par2, ter_par2]
        ) == parentheses_cfg.contains(
            [ter_par1, ter_par2, ter_par1, ter_par1, ter_par2, ter_par2]
        )
        assert wcnf_cfg.contains([ter_par1, ter_par1]) == parentheses_cfg.contains(
            [ter_par1, ter_par1]
        )

    test_regex()
    test_an_bn()
    test_removing_chain()
    test_balanced_parentheses()


def test_read_grammar_from_file():
    class TestCase:
        def __init__(self, path: str, good_tests: Iterable, bad_tests):
            self.path = path
            self.good_tests = good_tests
            self.bad_tests = bad_tests

    tests = []

    ter_a = Terminal("a")
    ter_b = Terminal("b")
    tests.append(
        TestCase(
            join("tests", "static", "balanced_parentheses.cfg"),
            [
                [ter_a, ter_b],
                [ter_a, ter_a, ter_b, ter_b],
                [ter_a, ter_b, ter_a, ter_b],
                [Epsilon()],
            ],
            [[ter_a], [ter_b, ter_b], [ter_a, ter_b, ter_a, ter_b, ter_a, ter_a]],
        )
    )

    tests.append(
        TestCase(
            join("tests", "static", "a_or_b.cfg"),
            [
                [ter_a, ter_b],
                [ter_a, ter_a, ter_b, ter_b],
                [ter_a, ter_b, ter_a, ter_b],
                [ter_a],
                [ter_b, ter_b],
                [ter_a, ter_b, ter_a, ter_b, ter_a, ter_a],
                [Epsilon()],
            ],
            [[Terminal("d")]],
        )
    )

    for test in tests:
        grammar = cfg.read_grammar_from_file(test.path)
        for good in test.good_tests:
            assert grammar.contains(good)

        for bad in test.bad_tests:
            assert not grammar.contains(bad)
