from pyformlang.cfg import CFG, Variable

from project.CFGConverter import CFGConverter


def cfg_to_wcnf(cfg: CFG) -> CFG:
    """Convert cfg to weak Chomsky normal form.

    Parameters
    ----------
    cfg : CFG
        Context Free Grammar.

    Returns
    -------
    converted_cfg : CFG
        Return cfg in weak Chomsky normal form.
    """
    if cfg.is_normal_form():
        return cfg

    cfg_converter = CFGConverter(cfg)
    return cfg_converter.to_wcnf()


def read_grammar_from_file(path: str, start: any = Variable("S")) -> CFG:
    """Read grammar from file

    Parameters
    ----------
    path : str
        Path to file.
    start : any
        Start non-terminal (variable)

    Returns
    -------
    cfg : CFG
        Return cfg.
    """

    with open(path, "r") as f:
        return CFG.from_text("\n".join(f.readlines()), start)
