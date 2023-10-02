from typing import Dict, List, Tuple, Union, Set

from scipy.sparse import kron, csr_array, csr_matrix, block_diag, lil_array, identity
from pyformlang.finite_automaton import (
    EpsilonNFA,
    State,
)


class Automaton:
    def __init__(
        self,
        start_states: set,
        final_states: set,
        states: set,
        symbols: set,
        symbol_matrices: Dict[any, csr_array],
        mapping: Dict[any, int],
    ):
        self.start_states: set = start_states
        self.final_states: set = final_states
        self.states = states
        self.symbols = symbols
        self.symbol_matrices = symbol_matrices
        self.old_state_to_new = mapping

    @classmethod
    def from_fa(cls, fa: any) -> "Automaton":
        """Turns the automaton into an adjacency matrix

        Parameters
        ----------
        fa : any
            Finite automaton from pyformlang

        Returns
        -------
        automaton : Automaton
        """
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

        return cls(
            fa.start_states, fa.final_states, fa.states, fa.symbols, result_map, mapping
        )

    def intersect(self, other: "Automaton") -> "Automaton":
        """Intersects two automata

        Parameters
        ----------
        other : Automaton

        Returns
        -------
        automaton : Automaton
            Returns the result intersection
        """

        # Kron product for each symbol
        result = {}
        symbols = self.symbols & other.symbols
        for symbol in symbols:
            symbol_matrix1 = self.symbol_matrices[symbol]
            symbol_matrix2 = other.symbol_matrices[symbol]
            result[symbol] = kron(symbol_matrix1, symbol_matrix2, format="csr")

        final_states = set()
        start_states = set()
        states = set()
        mapping = {}

        # Save start and final states for new automaton
        for state1, i1 in self.old_state_to_new.items():
            for state2, i2 in other.old_state_to_new.items():
                intersection_state = i1 * len(other.old_state_to_new) + i2
                mapping[intersection_state] = intersection_state
                states.add(intersection_state)

                if state1 in self.start_states and state2 in other.start_states:
                    start_states.add(intersection_state)

                if state1 in self.final_states and state2 in other.final_states:
                    final_states.add(intersection_state)

        return Automaton(start_states, final_states, states, symbols, result, mapping)

    def to_automata(self) -> EpsilonNFA:
        """Turns the automaton into a finite automaton from pyformlang

        Returns
        -------
        automaton : any
            Finite automaton from pyformlang
        """
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
        """Constructs a transitive closure of the automaton

        Returns
        -------
        adjacency_matrix : csr_matrix
            Returns transitive closure matrix
        """

        n = len(self.old_state_to_new)
        if len(self.symbol_matrices) == 0:
            return csr_array((n, n), dtype="bool")

        adj_matrix = sum(
            self.symbol_matrices.values(), start=csr_array((n, n), dtype="bool")
        )
        prev_nnz = adj_matrix.nnz
        curr_nnz = 0

        while prev_nnz != curr_nnz:
            adj_matrix += adj_matrix @ adj_matrix
            prev_nnz, curr_nnz = curr_nnz, adj_matrix.nnz

        return adj_matrix

    def _diagonal_sum(self, other: "Automaton") -> Dict[any, csr_matrix]:
        matrices = {}
        for symbol in self.symbols & other.symbols:
            matrices[symbol] = block_diag(
                (other.symbol_matrices[symbol], self.symbol_matrices[symbol]),
                format="csr",
            )
        return matrices

    def _create_front_matrix(self, regex: "Automaton") -> Tuple[csr_matrix, List[any]]:
        self_size = len(self.old_state_to_new)
        regex_size = len(regex.old_state_to_new)
        front = lil_array((regex_size, regex_size + self_size), dtype=bool)

        # Calculate start graph vertexes
        graph_start = lil_array([i in self.start_states for i in self.states])
        start_states = [regex.old_state_to_new[j] for j in regex.start_states]

        # Init front matrix
        for i in range(regex_size):
            front[i, i] = True
            if i in start_states:
                front[[i], regex_size:] = graph_start

        return front.tocsr()

    def _create_front_matrix_for_all_start_states(
        self, regex: "Automaton"
    ) -> Tuple[csr_matrix, List[any]]:
        self_size = len(self.old_state_to_new)
        regex_size = len(regex.old_state_to_new)
        start_states_num = len(self.start_states)
        front = lil_array(
            (start_states_num * regex_size, regex_size + self_size), dtype=bool
        )
        start_states = [regex.old_state_to_new[j] for j in regex.start_states]
        start_states_mapping = []
        for i, state in enumerate(self.start_states):
            start_states_mapping.append(self.old_state_to_new[state])
            start_state_matrix = lil_array(
                (regex_size, regex_size + self_size), dtype=bool
            )
            for j in range(regex_size):
                start_state_matrix[j, j] = True
                if j in start_states:
                    start_state_matrix[
                        j, regex_size + self.old_state_to_new[state]
                    ] = True

            front[i * regex_size : (i + 1) * regex_size, 0:] = start_state_matrix

        return front.tocsr(), start_states_mapping

    def bfs_rpq(
        self, regex: "Automaton", is_separately: bool
    ) -> Union[Set[any], Set[Tuple[any, any]]]:

        self_size = len(self.states)
        regex_size = len(regex.states)

        # Intersect symbols
        symbols = self.symbols & regex.symbols

        # Create a set of block-diagonal matrices
        matrices = self._diagonal_sum(regex)

        is_visited = None
        start_states_mapping = None

        # Create vector for initial states of both matrices
        if is_separately:
            (
                is_visited,
                start_states_mapping,
            ) = self._create_front_matrix_for_all_start_states(regex)
        else:
            is_visited = self._create_front_matrix(regex)

        # Starting bfs
        while True:
            old_is_visited = is_visited.nnz

            # Making bfs for each boolean matrix
            for symbol in symbols:
                result = is_visited @ matrices[symbol]
                transformed = _transform_to_new_front(result, regex_n=regex_size)
                is_visited += transformed

            if old_is_visited == is_visited.nnz:
                break

        result = set()
        regex_final = {regex.old_state_to_new[i] for i in regex.final_states}
        graph_final = {self.old_state_to_new[i] for i in self.final_states}
        rows, cols = is_visited.nonzero()
        for i, j in zip(rows, cols):
            f = j >= regex_size
            tmp1 = i % len(regex.final_states)
            s = i % len(regex.final_states) in regex_final
            tmp2 = j - regex_size
            t = j - regex_size in graph_final
            if (
                j >= regex_size
                and i % len(regex.states) in regex_final
                and j - regex_size in graph_final
            ):
                final = j - regex_size
                if is_separately:
                    result.add((start_states_mapping[i // len(regex.states)], final))
                else:
                    result.add(final)

        return result


def _column_boolean_addition(matrix: csr_matrix) -> csr_matrix:
    n, _ = matrix.shape
    result = csr_array(shape=(1, n))

    for _, j in zip(matrix.nonzero()):
        result[j] += True

    return result


def _create_init_front_matrix(graph_n: int, regex_n: int) -> csr_matrix:
    regex = identity(regex_n, format="csr", dtype=bool)
    graph = csr_array(shape=(graph_n, graph_n), dtype=bool)
    return block_diag((regex, graph), format="csr", dtype=bool)


def _transform_to_new_front(symbol_result: csr_matrix, regex_n: int) -> csr_matrix:

    new_front = lil_array(symbol_result.shape, dtype=bool)
    rows, cols = symbol_result.nonzero()
    for i, j in zip(rows, cols):
        if j < regex_n:
            row = symbol_result.getrow(i)
            if row.nnz > 1:
                new_front[[i // regex_n * regex_n + j], :] += row.tolil()

    return new_front.tocsr()
