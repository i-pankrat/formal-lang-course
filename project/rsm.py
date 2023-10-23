from project.ecfg import ECFG
from project.automaton_lib import regex_to_minimal_dfa

from typing import Dict

from pyformlang.cfg import Variable
from pyformlang.finite_automaton import EpsilonNFA


class RSM:
    def __init__(self, start: Variable, productions: Dict[Variable, EpsilonNFA]):
        self.start = start
        self.productions = productions

    @classmethod
    def from_ecfg(cls, ecfg: ECFG):
        cls(
            ecfg.start,
            {k: regex_to_minimal_dfa(r) for k, r in ecfg.productions.items()},
        )

    def minimize(self) -> "RSM":
        new_productions = {}
        for var, nfa in self.productions.items():
            new_productions[var] = nfa.minimize()

        return RSM(self.start, new_productions)
