from datatypes import *
from modules import *



COLLECTION: list[set[Item]] = []
GOTO: dict[int, dict[Terminal|Nonterminal, int]] = {}
X: set[tuple[int, Nonterminal]] = set()
CONFLICTS: str = ""

rules = list(e for opts in Module.grammar.values() for e in opts)



def CANONICAL(itemset: set[Item]) -> dict:
    """Compute the canonical LR(0) collection."""

    state = len(COLLECTION)
    GOTO[state] = {}
    COLLECTION.append(itemset)
    for token, closure in GOTOS(itemset).items():
        if closure in COLLECTION:
            GOTO[state][token] = COLLECTION.index(closure)
        else:
            GOTO[state][token] = len(COLLECTION)
            CANONICAL(closure)
        if isinstance(token, Nonterminal): X.add((state, token))


def CLOSURE(kernel: set[Item]) -> set[Item]:
    """Compute the closure of an LR(0) kernel."""

    closure = set()
    expansions = kernel
    while expansions:
        item = expansions.pop()
        if item not in closure:
            closure.add(item)
            if isinstance(item.current, Nonterminal):
                for production in Module.grammar[item.current]:
                    expansions.add(Item(0, production))
    return closure


def GOTOS(itemset: set[Item]) -> dict[Terminal|Nonterminal, set[Item]]:
    """Compute the goto transitions of a given state."""

    gotos: dict[Terminal|Nonterminal, set[Item]] = {}
    for item in itemset:
        if item.isReduction: continue
        if item.current not in gotos: gotos[item.current] = set()
        gotos[item.current].add(Item(item.dot+1, item.production))
    return { token : CLOSURE(kernel) for token, kernel in gotos.items() }


def ACCESSES(p: int, sequence: list[Terminal|Nonterminal]) -> int|None:
    """Applies a sequence of transitions from state p, returning the resultant state or `None`."""
    for t in sequence:
        try: p = GOTO[p][t]
        except: return None
    return p


def LOOKAHEADS() -> dict[tuple[int, Production], set[Terminal]]:
    """LALR lookahead computation algorithm, adapted from (DeRemer and Penello, 1982).
    Accessible via the ACM Digital Library: https://dl.acm.org/doi/epdf/10.1145/69622.357187.
    """
    
    DR: dict[tuple[int, Nonterminal], set[Terminal]] = { transition : set() for transition in X }
    reads: dict[tuple[int, Nonterminal], list[tuple[int, Nonterminal]]] = { transition : [] for transition in X }
    includes: dict[tuple[int, Nonterminal], list[tuple[int, Nonterminal]]] = { transition : [] for transition in X }
    lookback: dict[tuple[int, Production], list[tuple[int, Nonterminal]]] = {}
            
    for (p, A) in X:
        q = GOTO[p][A]
        for B in GOTO[q]:
            # direct read
            if isinstance(B, Terminal):
                DR[(p, A)].add(B)
            # reads relation
            elif isinstance(B, Nonterminal) and NULLABLE(B):
                reads[(p, A)].append((q, B))

        for production in Module.grammar[A]:
            # includes relation
            nullable = True
            # enumerating backwards allows us to stop iteration at the first nonnullable token
            for i, B in enumerate(reversed(production.pattern)):
                if isinstance(B, Nonterminal):
                    q = ACCESSES(p, production.pattern[:-(i+1)])
                    if q is not None: includes[(q, B)].append((p, A))
                    if not nullable: break
                    nullable = NULLABLE(B)
                else: break
            # lookback relation
            q = ACCESSES(p, production.pattern)
            if q is not None:
                if not (q, production) in lookback: lookback[(q, production)] = []
                lookback[(q, production)].append((p, A))


    Read = DIGRAPH(reads, DR)
    Follow = DIGRAPH(includes, Read)

    LA: dict[tuple, set] = {}
    for look, lookbacks in lookback.items():
        LA[look] = set()
        for back in lookbacks:
            LA[look].update(Follow[back])

    return LA


def DIGRAPH(
        R: dict[tuple[int, Nonterminal], list[tuple[int, Nonterminal]]], 
        f: dict[tuple[int, Nonterminal], set[Terminal]]
    ) -> dict[tuple[int, Nonterminal], set[Terminal]]:
    """The DeRemer-Penello Digraph algorithm.
    
    :param R: A relation on X.
    :param f: A set-valued function.
    :returns F: A function from X to sets."""

    F: dict[tuple[int, Nonterminal], set[Terminal]] = {}
    S: list[tuple[int, Nonterminal]] = []
    N: dict[tuple[int, Nonterminal], int] = dict.fromkeys(X, 0)
    
    def TRAVERSE(x):
        S.append(x)
        d = len(S)
        N[x] = d
        F[x] = f[x]
        for y in R[x]:
            if N[y] == 0: TRAVERSE(y)
            N[x] = min(N[x], N[y])
            F[x].update(F[y])
        if N[x] == d:
            while True:
                N[S[-1]] = float('inf')
                F[S[-1]] = F[x]
                if S.pop() == x: break

    for x in X:
        if N[x] == 0:
            TRAVERSE(x)

    return F


@functools.cache
def NULLABLE(rule: Terminal|Nonterminal, exclude: tuple = None) -> bool:
    exclude = exclude or tuple()
    return (
        isinstance(rule, Nonterminal)
        and any(
            (production.pattern == [])
            or all(NULLABLE(token, tuple((rule, *exclude))) for token in production.pattern if not token in exclude)
            for production in Module.grammar[rule]
        )
    )


def REDUCTIONS(p: int) -> dict:
    out = {}
    for item in COLLECTION[p]:
        if item.isReduction:
            lookaheads = LA.get((p, item.production))
            if not item.production in out: out[item.production] = set()
            if lookaheads is None:
                out[item.production].add(None)
            else:
                out[item.production].update(lookaheads)
    return out



CANONICAL(CLOSURE({ Item(0, Module.grammar[START()][0]) }))


LA: dict[tuple[int, Production], set[Terminal]] = LOOKAHEADS()
TABLE = {}
conflicts = {}


for p in range(len(COLLECTION)):
    TABLE[p] = {}
    for t, q in GOTO[p].items():
        if not t in TABLE[p]: TABLE[p][t] = []
        TABLE[p][t].append(-q)
    for A, lookaheads in REDUCTIONS(p).items():
        for t in lookaheads:
            if not t in TABLE[p]: TABLE[p][t] = []
            TABLE[p][t].append(rules.index(A))

    for token, actions in TABLE[p].items():            
        if len(actions) > 1:
            if not p in conflicts:
                conflicts[p] = {}

            conflict = "/".join(sorted(
                ((
                    "S" if action > 0 
                    else "R" if action < 0 
                    else "A"
                ) for action in TABLE[p][token]),
                reverse=True
            ))

            if not conflict in conflicts:
                conflicts[p][conflict] = []
            
            conflicts[p][conflict].append(token)

    if conflicts: 
        CONFLICTS = f"Found {len(conflicts)} conflicts."
        for p, conflictTypes in conflicts.items():
            for label, tokens in conflictTypes.items():
                CONFLICTS += f"\n(state {p}) {label} conflict on token{"s"*(len(tokens) != 1)} {", ".join(token.__repr__() for token in tokens)}"
    else:
        CONFLICTS = "No conflicts found."


if CONFIG.flags.verbose:
        print(CONFLICTS)
        print()

        from statistics import mean, median, mode
        sets = tuple(
            tuple(
                regex for regex in state.keys() 
                if isinstance(regex, Terminal) and not isinstance(regex, EOI)) for state in TABLE.values()
            )
        data = tuple(map(len, sets))

        print(f"""scanset optimization data

Original    : {len(Module.terminals)}
Average     : {mean(data):.3f}
Reduction   : {(1-mean(data)/len(Module.terminals))*100:.3f}%

Minimum     : {min(data)}
Median      : {median(data)}
Maximum     : {max(data)}

Mode : {mode(data)}

NULLABLE cache: {NULLABLE.cache_info()}
""")


Module.grammar = f"""--------{{ Module.grammar }}--------
{"\n".join(f"Rule {i:<3} {str(rule)}" for i, rule in enumerate(rules))}"""

if CONFIG.flags.debug: 
    print(Module.grammar)
    print()

    categories = [*sorted(Module.terminals, key=str), EOI(), *Module.grammar.keys()]
    categories.remove(START())
    parsetable = displayTable(
        title="LALR Table", 
        columns=dict.fromkeys(("State", *map(str, categories)), {})
        )
    for state, options in TABLE.items():
        row = [str(state)]
        for token in categories:
            data = options.get(token, [None])[0]
            action = (
            "ERR" if data is None
            else "S" if data > 0
            else "R" if data < 0
            else "ACC"
            )
            if data: data = str(abs(data))
            row.append("" if data is None else f"{action} {data}")
        parsetable.add_row(*row)
        
    
    print("------{ AUTOMATON }------")
    for p, closure in enumerate(COLLECTION):
        print(f"State {p}")
        for item in closure:
            print(f"    {item}")
        print()

    print(parsetable)


# @functools.cache
def parsetable_to_str() -> str:
    return f"""


##### PARSETABLE #####



# {str(Module.grammar).replace("\n", "\n# ")}



# Parsetable constructed with {len(TABLE)} state{"s"*(len(TABLE)!=1)}.
# {CONFLICTS.replace("\n", "\n# ")}



indentation = {Module.indentation}
newlines = {Module.newlines}
definitions = {{
    {",\n    ".join(f"'{k}' : r\"{v}\"" for k, v in Module.definitions.items())}
}}



rules = (
    {",\n    ".join(rule.__repr__() for rule in rules)}
)



table = {{
    {",\n    ".join(f"""{state} : {{
        {",\n        ".join(f"{token.__repr__()} : {actions}" for token, actions in transitions.items())}
    }}""" for state, transitions in TABLE.items())}
}}"""


def transform_semantics(filename: str, modulename: str) -> str:
    from re import Match
    from re import sub

    def replace_fname(match: Match) -> str:
        return f"p_{modulename}_{match.group().removeprefix("p_")}".lower()

    with open(filename) as file:
        return sub(
            pattern=r"p_\w*\(",
            repl=replace_fname,
            string=file.read()
        )
