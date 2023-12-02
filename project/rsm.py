from project.ecfg import ECFG

from typing import Dict

from pyformlang.cfg import Variable
from pyformlang.finite_automaton import EpsilonNFA


class RSM:
    def __init__(self, start: Variable, productions: Dict[Variable, EpsilonNFA]):
        self.start = start
        self.productions = productions

    @classmethod
    def from_ecfg(cls, ecfg: ECFG) -> "RSM":
        """Create rsm from ecfg

        Parameters
        ----------
        ecfg : ECFG
            Extended Context-Free Grammars

        Returns
        -------
        rsm : RSM
            Returns rsm obtained from ecfg
        """
        return cls(
            ecfg.start,
            {
                k: r.to_epsilon_nfa().to_deterministic()
                for k, r in ecfg.productions.items()
            },
        )

    def minimize(self) -> "RSM":
        """Minimize finite automates of rsm

        Returns
        -------
        rsm : Rsm
            Returns minimized rsm
        """
        new_productions = {}
        for var, nfa in self.productions.items():
            new_productions[var] = nfa.minimize()

        return RSM(self.start, new_productions)
