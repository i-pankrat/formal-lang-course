import pathlib

from pyformlang.cfg import CFG, Variable


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

    new_cfg = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )

    new_productions = new_cfg._get_productions_with_only_single_terminals()
    new_productions = new_cfg._decompose_productions(new_productions)

    return CFG(
        new_cfg.variables, new_cfg.terminals, new_cfg.start_symbol, set(new_productions)
    )


def read_grammar_from_file(path: str | pathlib.Path, start: any = Variable("S")) -> CFG:
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
