from project.ecfg import ECFG
from project.cfg import read_grammar_from_file


def test_ecfg_from_cfg():
    test_files = ["balanced_parentheses", "a_or_b"]

    for filename in test_files:
        cfg = read_grammar_from_file("tests/static/" + filename + ".cfg")
        ecfg = ECFG.from_cfg(cfg)
        assert ecfg.start == cfg.start_symbol
        assert len(ecfg.productions) == 1
