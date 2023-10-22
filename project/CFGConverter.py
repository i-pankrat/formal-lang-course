from pyformlang.cfg import CFG, Variable, Production


class CFGConverter:
    def __init__(self, cfg: CFG):
        self.variables = set(cfg.variables)
        self.terminals = set(cfg.terminals)
        self.productions = set(cfg.productions)
        self.start_symbol = cfg.start_symbol
        self.counter = 0

    def _fresh_var(self, var: Variable) -> Variable:
        """Generate fresh variable name

        Parameters
        ----------
        var : Variable
            var on the basis of which a new variable will be created

        Returns
        -------
        var : Variable
            Return fresh variable.
        """

        while Variable(str(var.value) + str(self.counter)) in self.variables:
            self.counter += 1

        res = Variable(str(var.value) + str(self.counter))
        self.counter += 1
        return res

    def to_cfg(self) -> CFG:
        """Convert CFGConverter to CFG

        Returns
        -------
        cfg : CFG
            Returns context free grammar.
        """
        return CFG(self.variables, self.terminals, self.start_symbol, self.productions)

    def to_wcnf(self) -> CFG:
        """Convert CFGConverter to CFG in weak Chomsky normal form.

        Returns
        -------
        cfg : CFG
            Returns cfg in weak Chomsky normal form.
        """
        new_productions = set()

        # 1. Remove all productions with body length > 2
        for prod in self.productions:
            if len(prod.body) > 2:
                curr_head = prod.head
                prod_len = len(prod.body)
                # Create new products with length 2 to replace long production
                for i in range(prod_len - 2):
                    var = self._fresh_var(prod.head)
                    self.variables.add(var)
                    new_productions.add(Production(curr_head, [prod.body[i], var]))
                    curr_head = var

                new_productions.add(
                    Production(
                        curr_head, [prod.body[prod_len - 2], prod.body[prod_len - 1]]
                    )
                )
            else:
                new_productions.add(prod)

        # 2. Remove chain rules
        self.productions = new_productions
        cfg = CFG(self.variables, self.terminals, self.start_symbol, self.productions)
        cfg = (
            cfg.remove_useless_symbols()
            .eliminate_unit_productions()
            .remove_useless_symbols()
        )

        # 3. Replace the following rules (-> t1 t2; ->N1 t1; ->t1 N2)
        new_productions = set()
        self.variables = set(cfg.variables)
        self.terminals = set(cfg.terminals)
        self.productions = set(cfg.productions)
        self.start_symbol = cfg.start_symbol

        for prod in self.productions:
            if len(prod.body) == 2:

                if prod.body[0] in self.terminals and prod.body[1] in self.terminals:
                    fv1 = self._fresh_var(prod.head)
                    self.variables.add(fv1)
                    fv2 = self._fresh_var(prod.head)
                    self.variables.add(fv2)
                    new_productions.add(Production(prod.head, [fv1, fv2]))
                    new_productions.add(Production(fv1, [prod.body[0]]))
                    new_productions.add(Production(fv2, [prod.body[1]]))
                elif prod.body[0] in self.variables and prod.body[1] in self.terminals:
                    fv = self._fresh_var(prod.head)
                    self.variables.add(fv)
                    new_productions.add(Production(prod.head, [prod.body[0], fv]))
                    new_productions.add(Production(fv, [prod.body[1]]))
                elif prod.body[0] in self.terminals and prod.body[1] in self.variables:
                    fv = self._fresh_var(prod.head)
                    self.variables.add(fv)
                    new_productions.add(Production(prod.head, [fv, prod.body[1]]))
                    new_productions.add(Production(fv, [prod.body[0]]))
                else:
                    new_productions.add(prod)
            else:
                new_productions.add(prod)

        self.productions = new_productions
        return self.to_cfg()
