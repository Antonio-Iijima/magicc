from utils import *
from datatypes import *



def parse(expr: str, state_limit: int = 2**100, dFlag: bool = False) -> Parsed:
    from AST import (
        expects, expected_patterns,
        PROGRAM, K, 
        EXPECTED_TOKENS,
        EXPECTED_PATTERNS
    )

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

        if dFlag: print("Current states", current_states)

        # We need to iteratively reduce all states as far as possible,
        # adding valid future states to the list as appropriate.
        while reducible_states:

            state = reducible_states.pop()
            
            if dFlag: print("State", state)

            for (rule, module, variant, pattern) in expected_patterns(state[-1]):

                idx = len(state) - len(pattern)
                reducible = state[idx:]

                # Reduce only if pattern matches the reducible part of the state.
                if list(map(type, reducible)) == pattern:

                    reduced = State(state[:idx] + [rule(reducible, module, variant)])

                    if dFlag: print("Reduced", reduced)

                    reducible_states.add(reduced)
                    
                    # Accept as future state if the following:
                    # 1) EOI (no next token) or next token is expected
                    # 2) Each token correctly expects the next token
                    if (
                        (
                            next_token == None
                            or expects(reduced[-1], next_token)
                        ) and (
                            all(idx == k or expects(reduced[idx-k-1], reduced[idx-k]) 
                                for k in range(min(K, len(reduced))))
                        )
                    ):
                        if dFlag: print("Future", reduced)
                        future_states.add(reduced)

                # If the current pattern does not match, but could match if given more tokens.
                # elif type(state[-1]) in pattern: future_states.add(state)

        max_states = max(max_states, len(future_states))
        if max_states > state_limit: raise RuntimeError(f"Too many states to consider: {max_states}")
        
        current_states, future_states = future_states or current_states, OrderedSet()

        if dFlag: 
            print("Future states", current_states)
            print()
            

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
        print(f"WARNING: multiple valid parses found (ambiguous grammar)")
        print(f"Using highest depth parse tree:", max(accepting_states, key=lambda state: state.depth()).depth(), "levels")

    return Parsed(expr, max(accepting_states, key=lambda state: state.depth()), max_states, showTree=dFlag)


def tokenize(string: str) -> list:
    from AST import TERMINALS, INDENT_SENSITIVE
    
    lines = preprocess_input(string, INDENT_SENSITIVE)
    
    original = string = "\n".join((line for line in lines if line.strip())).strip()

    tokens = []

    while string:
        matches = []
        
        for rule, (module, regex) in TERMINALS.items():
            match = regex.match(string)
            if match: matches.append((match.group(), rule, module))

        if not matches: raise SyntaxError(f"index {len(original)-len(string)}: unrecognized token '{string[0]}' in input '{original}'")
        
        match, rule, module = max(matches, key=lambda tup: len(tup[0]))
        tokens.append(rule([match], module))
        string = string.removeprefix(match).lstrip(" ")

    filtered = list(filter(None, tokens))

    return filtered
 

def indent(lines: list) -> list:
    indented = []
    curr_indent = prev_indent = 0

    for i, line in enumerate(lines):
        
        # Remove commented and empty lines
        if (not line.strip()) or line.strip().startswith("#"): 
            continue

        while line.startswith(get_config("special", "indentation")):
            line = line.removeprefix(get_config("special", "indentation"))
            curr_indent += 1

        if line.startswith(" "): 
            count = line.count(" ", 0, 2)
            raise IndentationError(f"invalid indent in line {i+1}: {count} extra space{"" if count == 1 else "s"}.")

        diff = curr_indent - prev_indent

        while diff < 0:
            indented[-1] += get_config("special", "dedent")
            diff += 1

        # Newline will come after DEDENTs but before INDENTS
        indented.append("")
        
        while diff > 0:
            indented[-1] += get_config("special", "indent")
            diff -= 1
            
        indented[-1] += line
        prev_indent, curr_indent = curr_indent, 0

    # Handle any final DEDENTs
    while prev_indent > 0:
        indented[-1] += get_config("special", "dedent")
        prev_indent -= 1

    return indented


def preprocess_input(string: str, indentSensitive: bool) -> list:
    """Strips # comments and wraps automatic indentation processing."""

    lines = string.splitlines()

    for i, line in enumerate(lines):
        if "#" in line:
            lines[i] = line[:line.index("#")]

    return indent(lines) if indentSensitive else lines
