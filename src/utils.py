from io import TextIOWrapper

import re

from rich import print



LIB_PATH = ".lib"



def preprocess_text(text: TextIOWrapper) -> list[str]: 
    return [line for line in text.read().splitlines() if line.strip() and not line.startswith("--")]


def is_nonterminal(prod: str) -> bool: 
    return isinstance(prod, str) and re.fullmatch(r"<.*>", prod)


def is_terminal(prod: str) -> bool: 
    return not is_nonterminal(prod)


def comparative(x): 
    return x if isinstance(x, str) else x.__name__


def compare(a: list, b: list) -> bool:
    """Check if all the elements of `a` and `b` match."""
    return len(a) == len(b) and all(comparative(x) == comparative(y) for x, y in zip(a, b))


def get_input(prompt: str = "", s: str = "") -> str:
    if s.endswith("\nquit"):
        from sys import exit
        exit()
    if s.endswith("\n"):
        return s
    return get_input("." * (len(prompt)-1) + " ", s + "\n" + input(prompt))


def regularize(path, sep="::="):
    with open(path) as file:
        text = file.readlines()
    
    offset = 0

    for i, line in enumerate(s.strip() for s in text):
        text[i] = [s.strip() for s in line.split(sep)]
        if len(text[i]) == 2:
            offset = max(offset, len(text[i][0]))

    for i, line in enumerate(text):
        if isinstance(line, list):
            if len(line) == 1: 
                text[i] = line[0]
            else:
                rule, production = line
                text[i] = f"{rule.upper()}{" " * (offset-len(rule))} ::= {" ".join([s.upper() if (len(s) > 1 and s[::len(s)-1] == "<>") else s for s in production.split()])}"

    text = "\n".join(text).strip() + "\n"

    with open(path, "w") as file:
        file.write(text)

# Grammar post-processing/expansion
# for rule, alternatives in GRAMMAR.items():
#     GRAMMAR[rule] = []

#     for variant, pattern in enumerate(alternatives):
#         # Expand nullable patterns
#         expanded_null_patterns = [[]]
#         for i, token in enumerate(pattern):
#             if not token == EPSILON:
#                 expanded_null_patterns = list(state + [token] for state in expanded_null_patterns)
#                 if nullable(token):
#                     expanded_null_patterns += list(state[:-1] for state in expanded_null_patterns)

#         for expanded_null_pattern in expanded_null_patterns:
#             if expanded_null_pattern and not (
#                 expanded_null_pattern in GRAMMAR[rule]
#                 or len(expanded_null_pattern) == 1 and expanded_null_pattern[0] == rule
#             ):
#                 GRAMMAR[rule].append([variant] + expanded_null_pattern)

# # Only construct expected tokens/patterns with the full expansion of the grammar
# for rule, alternatives in GRAMMAR.items():                
#     for pattern in alternatives:
#         variant = pattern.pop(0)

#         # Expand expected patterns 
#         for token in pattern:
#             if not (rule, variant, pattern) in EXPECTED_PATTERNS[token]: 
#                 EXPECTED_PATTERNS[token].append((rule, variant, pattern))

# for rule, alternatives in GRAMMAR.items():                
#     for pattern in alternatives:
    
#         # Expand expected tokens
#         for i, token in enumerate(pattern[:-1]):
#             expand_expected(token, pattern[i+1])



def find_nullable_rules(grammar: dict) -> set:
    """Collect nullable rules (i.e. rules that can be expanded from EPSILON)."""

    nulls = set()
    count = 0
    
    while count < len(nulls):
        for rule, alternatives in grammar.items():
            for pattern in alternatives:
                if (
                    len(pattern) == 1
                    and pattern[0] in nulls
                    and rule not in nulls
                ):
                    nulls.add(rule)
        count += 1

    return nulls


def build_expected_tokens(grammar: dict, nulla: set) -> dict:
    """Constructs a dictionary mapping every token to a set of all possible subsequent tokens."""

    for rule, alternatives in grammar.items():
        grammar[rule] = []

        for variant, pattern in enumerate(alternatives):
            # Expand nullable patterns
            expanded_null_patterns = [[]]
            for i, token in enumerate(pattern):
                if not token == "e":
                    expanded_null_patterns = list(state + [token] for state in expanded_null_patterns)
                    if token in nulla:
                        expanded_null_patterns += list(state[:-1] for state in expanded_null_patterns)

            for expanded_null_pattern in expanded_null_patterns:
                if expanded_null_pattern and not (
                    expanded_null_pattern in grammar[rule]
                    or len(expanded_null_pattern) == 1 and expanded_null_pattern[0] == rule
                ):
                    grammar[rule].append([variant] + expanded_null_pattern)
                    
    print(grammar)

    return grammar


def build_expected_patterns(grammar: dict):

    expected_patterns = {}

    for rule, alternatives in grammar.items():

        for pattern in alternatives:
            if not (len(pattern) == 1 and isinstance(pattern[0], str)):
                for curr, next in zip(pattern[:-1], pattern[1:]):
                    expected_patterns[curr] = expected_patterns.get(curr, []) + [grammar[next]]

    print(expected_patterns)

    return expected_patterns



if __name__ == "__main__":
    from sys import argv

    regularize(argv[-1] + "/syntax.txt")
