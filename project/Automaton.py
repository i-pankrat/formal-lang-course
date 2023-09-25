from typing import Dict

from scipy.sparse import kron, csr_array, csr_matrix
from pyformlang.finite_automaton import (
    EpsilonNFA,
    State,
)


class Automaton:
    def __init__(self, start_states: set, final_states: set, symbols: set, symbol_matrices: Dict[any, csr_array],
                 mapping: Dict[any, int]):
        self.start_states: set = start_states
        self.final_states: set = final_states
        self.symbols = symbols
        self.symbol_matrices = symbol_matrices
        self.old_state_to_new = mapping

    @classmethod
    def from_fa(cls, fa: EpsilonNFA) -> "Automaton":
        mapping = {state: i for i, state in enumerate(fa.states)}
        symbol_to_data = {}

        # Prepare data for creating scipy.sparse adjacency matrix for each symbol
        for state1, symbol, state2 in fa:
            map_state1 = mapping[state1]
            map_state2 = mapping[state2]

            if symbol in symbol_to_data:
                row, col, data = symbol_to_data[symbol]
                row.append(map_state1)
                col.append(map_state2)
                data.append(True)
            else:
                symbol_to_data[symbol] = ([map_state1], [map_state2], [True])

        # Creating scipy.sparse adjacency matrix for each symbol
        result_map = {}
        shape = (len(mapping), len(mapping))
        for k, v in symbol_to_data.items():
            row, col, data = v
            result_map[k] = csr_array((data, (row, col)), shape=shape)

        return cls(fa.start_states, fa.final_states, fa.symbols, result_map, mapping)

    def intersect(self, other: "Automaton") -> "Automaton":

        # Kron product for each symbol
        result = {}
        symbols = self.symbols & other.symbols
        for symbol in symbols:
            symbol_matrix1 = self.symbol_matrices[symbol]
            symbol_matrix2 = other.symbol_matrices[symbol]
            result[symbol] = kron(symbol_matrix1, symbol_matrix2, format="csr")

        final_states = set()
        start_states = set()
        mapping = {}

        # Save start and final states for new automaton
        for state1, i1 in self.old_state_to_new.items():
            for state2, i2 in other.old_state_to_new.items():
                intersection_state = i1 * len(other.old_state_to_new) + i2
                mapping[intersection_state] = intersection_state

                if state1 in self.start_states and state2 in other.start_states:
                    start_states.add(intersection_state)

                if state1 in self.final_states and state2 in other.final_states:
                    final_states.add(intersection_state)

        return Automaton(start_states, final_states, symbols, result, mapping)

    def to_automata(self) -> EpsilonNFA:
        fa = EpsilonNFA()

        # Add transition to automaton of intersection
        for symbol, adj_matrix in self.symbol_matrices.items():
            rows, cols = adj_matrix.nonzero()
            for i, j in zip(rows, cols):
                fa.add_transition(State(i), symbol, State(j))

        # Make states final and start
        for state in self.start_states:
            fa.add_start_state(state)

        for state in self.final_states:
            fa.add_final_state(state)

        return fa

    def transitive_closure(self) -> csr_matrix:
        n = len(self.old_state_to_new)
        if len(self.symbol_matrices) == 0:
            return csr_array((n, n), dtype="bool")

        adj_matrix = sum(self.symbol_matrices.values(), start=csr_array((n, n), dtype="bool"))
        prev_nnz = adj_matrix.nnz
        curr_nnz = 0

        while prev_nnz != curr_nnz:
            adj_matrix += adj_matrix @ adj_matrix
            prev_nnz, curr_nnz = curr_nnz, adj_matrix.nnz

        return adj_matrix
