from typing import AbstractSet, Dict

from pyformlang.cfg import CFG, Variable, Terminal
from pyformlang.regular_expression import Regex


class ECFG:
    def __init__(
        self,
        start: Variable,
        terminals: AbstractSet[Terminal],
        variables: AbstractSet[Variable],
        productions: Dict[Variable, Regex],
    ):
        self.start = start
        self.terminals = set(terminals)
        self.variables = set(variables)
        self.productions = productions

    @classmethod
    def from_cfg(cls, cfg: CFG):
        productions = {}

        for prod in cfg.productions:
            regex_body = Regex(
                "".join([o.value for o in prod.body] if len(prod.body) > 0 else "$")
            )
            if prod.head in productions:
                productions[prod.head] = productions[prod.head].union(regex_body)
            else:
                productions[prod.head] = regex_body

        return cls(cfg.start_symbol, cfg.terminals, cfg.variables, productions)
