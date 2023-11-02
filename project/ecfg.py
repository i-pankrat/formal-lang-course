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

    @classmethod
    def from_text(cls, x: str, start: any = Variable("S")):
        productions = {}
        ecfg_rules = [rule for rule in x.split("\n") if not rule]
        for rule in ecfg_rules:
            separated_rule = rule.split("->")
            if len(separated_rule) != 2:
                raise SyntaxError(
                    "Invalid ecfg grammar: incorrect rule format, expected '->'"
                )

            separated_rule[0] = separated_rule[0].strip()
            separated_rule[1] = separated_rule[1].strip()

            if separated_rule[0] in productions:
                raise SyntaxError(
                    "Invalid ecfg grammar: there is more than one rule for one variable"
                )

            productions[Variable(separated_rule[0])] = Regex(separated_rule[1])

        return ECFG(start, productions)

    @classmethod
    def from_file(cls, file_name: str, start: any = Variable("S")):
        with open(file_name) as file:
            return ECFG.from_text(file.read(), start)
