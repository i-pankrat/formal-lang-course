from pyformlang.cfg import CFG

from project.CFGConverter import CFGConverter


def cfg_to_wcnf(cfg: CFG) -> CFG:
    if cfg.is_normal_form():
        return cfg

    cfg_converter = CFGConverter(cfg)
    return cfg_converter.to_wcnf()
