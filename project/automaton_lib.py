from typing import List, Optional

from project.Automaton import Automaton

from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    EpsilonNFA,
    State,
)


def regex_to_minimal_dfa(regex: Regex) -> DeterministicFiniteAutomaton:
    """Convert regular expression to minimal deterministic finite automaton

    Parameters
    ----------
    regex : Regex
        Regular expression.

    Returns
    -------
    dfa : DeterministicFiniteAutomaton
        Deterministic finite automaton obtained from the regular expression.
    """

    return regex.to_epsilon_nfa().minimize()


def graph_to_nfa(
    graph: any,
    start_states: Optional[List[State]],
    final_states: Optional[List[State]],
) -> NondeterministicFiniteAutomaton:

    """Convert graph to nondeterministic finite automaton

    Parameters
    ----------
    graph : any
        Graph from networkx
    start_states: Optional[List[State]]
        Start states of nondeterministic finite automaton
    final_states: Optional[List[State]]
        Final states of nondeterministic finite automaton

    Returns
    -------
    nfa : NondeterministicFiniteAutomaton
        Nondeterministic finite automaton obtained from the graph.
    """

    nfa = EpsilonNFA.from_networkx(graph)

    if start_states:
        for state in start_states:
            nfa.add_start_state(state)
    else:
        for state in nfa.states:
            nfa.add_start_state(state)

    if final_states:
        for state in final_states:
            nfa.add_final_state(state)
    else:
        for state in nfa.states:
            nfa.add_final_state(state)
    return nfa.remove_epsilon_transitions()


def intersect_two_finite_automatons(first_fa: any, second_fa: any) -> any:

    """Computes the intersection of two automata

    Parameters
    ----------
    first_fa : any
        Finite automaton from pyformlang
    second_fa: Optional[List[State]]
        Finite automaton from pyformlang

    Returns
    -------
    fa : any
        Returns an intersection automaton from pyformlang
    """

    first_automaton = Automaton.from_fa(first_fa)
    second_automaton = Automaton.from_fa(second_fa)
    intersection_automaton = first_automaton.intersect(second_automaton)
    return intersection_automaton.to_automata()
