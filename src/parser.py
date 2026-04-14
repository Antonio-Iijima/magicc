from utils import *
from datatypes import *



def parse(expr: str, state_limit: int = 2**100) -> Parsed:
    from AST import (
        expects, expected_patterns,
        PROGRAM, K, 
        EXPECTED_TOKENS,
        EXPECTED_PATTERNS
    )

    dFlag = get_config("flags", "debug")

    remaining_tokens = tokenize(expr)
    tokens = []

    current_states = OrderedSet((State(),))
    future_states = OrderedSet()

    if dFlag:
        print("EXPECTED TOKENS:")
        for key, expected in sorted(EXPECTED_TOKENS.items(), key=lambda x: str(x)):
            print(key, end=" :: ")
            print(expected)
            print()

        print()
        
        print("EXPECTED PATTERNS:")
        for key, expected in sorted(EXPECTED_PATTERNS.items(), key=lambda x: str(x)):
            print(key, end=" :: ")
            print(expected)
            print()

        print()

    max_states = 0

    # Process tokens sequentially, pursuing all valid shift/reduce paths in parallel.
    while remaining_tokens:
        token = remaining_tokens.pop(0)

        # Otherwise set up to process states at this token
        tokens.append(token)

        next_token = remaining_tokens[0] if remaining_tokens else None

        for state in current_states: state.append(token)
        
        reducible_states = current_states.copy()

        # We need to iteratively reduce all states as far as possible,
        # adding valid future states to the list as appropriate.
        while reducible_states:

            state = reducible_states.pop()
            
            if dFlag: print("State", stringify(state))

            for (rule, module, variant, pattern) in expected_patterns(state[-1]):

                idx = len(state) - len(pattern)
                reducible = state[idx:]

                # Reduce only if pattern matches the reducible part of the state.
                if list(map(type, reducible)) == pattern:

                    reduced = State(state[:idx] + [rule(reducible, module, variant)])

                    if dFlag: print("Reduced", stringify(reduced))

                    reducible_states.add(reduced)
                    
                    # Accept as future state if the following:
                    # 1) EOI (no next token) or next token is expected
                    # 2) Each token correctly expects the next token
                    if (
                        expects(reduced[-1], next_token)
                        and (
                            all(idx == k or expects(reduced[idx-k-1], reduced[idx-k]) 
                                for k in range(min(K, len(reduced))))
                        )
                    ):
                        if dFlag: print("Future", stringify(reduced)) or print()
                        future_states.add(reduced)
 
                # If the current pattern does not match, but could match if given more tokens.
                # elif (
                #     (type(state[-1]) in pattern)
                #     and (expects(state[-1], next_token))
                # ): 
                #     future_states.add(state)

        max_states = max(max_states, len(future_states))
        if max_states > state_limit: raise RuntimeError(f"Too many states to consider: {max_states}")
        
        current_states, future_states = future_states or current_states, OrderedSet()

    accepting_states: OrderedSet = OrderedSet(
        state[0] for state in current_states if (
            len(state) == 1
            and isinstance(state[0], PROGRAM)
        ))
    
    if dFlag:
        print()
        print(list(str(state) for state in accepting_states))
    
    if not accepting_states: 
        raise SyntaxError("parser terminated without any accepting states.")
    
    if (len(accepting_states) > 1):
        accepted = min(accepting_states, key=lambda state: state.depth())
        print(f"WARNING: {len(accepting_states)} parse trees found (ambiguous grammar)")
        print(f"Resolving for minimum depth parse tree (d={accepted.depth()})")
    else: accepted = accepting_states.pop()

    return Parsed(expr, accepted, max_states)


def tokenize(unprocessed: str) -> list:
    from AST import TERMINALS
    
    string = preprocess_input(unprocessed)

    past = ""

    tokens = []

    while string:
        matches = []
        
        for rule, (module, regex) in TERMINALS.items():
            match = regex.match(string)
            if match: matches.append((match.group(), rule, module))

        if not matches: 
            raise SyntaxError(f"line {past.count("\n")+1}, unrecognized token '{string[0]}'")

        match, rule, module = max(matches, key=lambda tup: len(tup[0]))
                
        if (tokens or ("\n" not in match)): tokens.append(rule([match], module))
        
        string = string.removeprefix(match).lstrip(" ")
        past += match

    filtered = list(filter(None, tokens))

    return filtered


def autoIndent(lines: list[str]) -> list:
    indented = []
    emptyLines = []
    curr_indent = prev_indent = 0

    levels = list((len(line)-len(line.lstrip(" "))) for line in lines)
    level = max(set(levels).difference({0}) or {1}, key=lambda val: levels.count(val))

    indentation = " " * level
    formatting = get_config("formatting")
    indent, dedent = formatting["indent"], formatting["dedent"]

    for i, line in enumerate(lines):
        
        if (not line.strip()):
            emptyLines.append(line)
            continue

        while line.startswith(indentation):
            line = line.removeprefix(indentation)
            curr_indent += 1

        if line.startswith(" "): 
            expected = (len(line)-len(line.lstrip(" ")))%level
            raise IndentationError(f"line {i+1}, {expected} space{"s" * (expected != 1)}.")

        diff = curr_indent - prev_indent

        while diff < 0:
            indented[-1] += dedent
            diff += 1

        # Newline will come after DEDENTs but before INDENTS
        indented.extend(emptyLines)
        indented.append("")
        
        while diff > 0:
            indented[-1] += indent
            diff -= 1
            
        indented[-1] += line
        emptyLines = []
        prev_indent, curr_indent = curr_indent, 0

    # Handle any final DEDENTs
    while prev_indent > 0:
        indented[-1] += dedent
        prev_indent -= 1

    return indented


def preprocess_input(string: str) -> list:
    """Strips # comments and wraps automatic indentation processing."""

    lines = string.splitlines()

    for i, line in enumerate(lines):
        if "#" in line:
            lines[i] = line[:line.index("#")]

    formatting = get_config("formatting")
    indentation, newlines = formatting["indentation"], formatting["newlines"]

    return (
        "\n".join(autoIndent(lines)) if indentation
        else ("\n" if newlines else " ").join(lines).strip()
    )
