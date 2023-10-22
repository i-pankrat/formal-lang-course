from pyformlang.cfg import CFG, Variable

from project.CFGConverter import CFGConverter


def cfg_to_wcnf(cfg: CFG) -> CFG:
    if cfg.is_normal_form():
        return cfg

    cfg_converter = CFGConverter(cfg)
    return cfg_converter.to_wcnf()


def read_grammar_from_file(path: str, start: any = Variable("S")) -> CFG:

    with open(path, "r") as f:
        return CFG.from_text("\n".join(f.readlines()), start)
