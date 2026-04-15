from io import TextIOWrapper
from json import load, dump

import re
import os



def get_config(*keys): 
    """Look up a value from the config, applying keys sequentially.
    No arguments returns the config itself."""
    
    with open(os.path.join(os.path.dirname(__file__), "config.json")) as file:
        cfg = load(file)

    for key in keys: cfg = cfg[key]

    return cfg


def set_config(cfg: dict, indent: int = 3):
    """Writes a provided `dict` to the config.json file."""
    
    with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as file:
        dump(cfg, file, indent=indent)


def preprocess_text(text: TextIOWrapper) -> list[str]: 
    return [line for line in text.read().splitlines() if line.strip() and not line.startswith("--")]


def is_nonterminal(prod: str) -> bool: 
    return isinstance(prod, str) and re.fullmatch(r"<.*>", prod)


def is_terminal(prod: str) -> bool: 
    return not is_nonterminal(prod)


def get_input(prompt: str = "", s: str = "") -> str:
    if s.endswith("\nquit"):
        from sys import exit
        exit()
    
    elif s.endswith("\nclear"):
        from os import system, name as OS
        system('cls' if OS == 'nt' else 'clear')
        print(f"magicc v{get_config("version")} </> {get_config("language")} {get_config("implementation")}")
        return ""
    
    elif s.endswith("\n"):
        return s
    
    return get_input("." * (len(prompt)-1) + " ", s + "\n" + input(prompt))


def regularize(path):
    if os.path.isdir(path):
        for file in os.listdir(path):
            regularize(os.path.join(path, file))
            
    elif path.endswith(".txt"):
        print(f"Regularizing {path}")
        
        with open(path) as file:
            text = file.read()
            text = text.splitlines()
        
        offset = 0

        for i, line in enumerate(s.strip() for s in text):
            text[i] = [s.strip() for s in line.split("::=")]
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


def find_nullable_rules(grammar: dict) -> set:
    """Collect nullable rules (i.e. rules that can be expanded from EPSILON)."""

    nulls = {"ε"}

    count = 0
    
    while count < len(nulls):
        for rule, modules in grammar.items():
            for _, alternatives in modules.items():
                for pattern in alternatives:
                    if (
                        len(pattern) == 1
                        and pattern[0] in nulls
                        and rule not in nulls
                    ):
                        nulls.add(rule)
        count += 1

    return nulls


def eliminate_nulls(grammar: dict, nulls: set) -> dict:

    for rule, modules in list(grammar.items()):
        for module, alternatives in list(modules.items()):
            
            grammar[rule][module] = []
            
            for variant, pattern in enumerate(alternatives):
                expanded_null_patterns = [(variant, [])]
                
                for token in pattern:

                    # For non-epsilon tokens, append to each state;
                    # if token is nullable, also add a new alternative where it is not included. 
                    if not token == "ε":
                        expanded_null_patterns = list((variant, state + [token]) for (variant, state) in expanded_null_patterns)
                        if token in nulls:
                            expanded_null_patterns += list((variant, state[:-1]) for (variant, state) in expanded_null_patterns)

                # Filter out duplicates / infinite recursion
                for (variant, expanded_null_pattern) in expanded_null_patterns:
                    
                    if expanded_null_pattern and not (
                        expanded_null_pattern in grammar[rule][module]
                        or len(expanded_null_pattern) == 1 and expanded_null_pattern[0] == rule
                    ):
                        grammar[rule][module].append((variant, expanded_null_pattern))
            
            if not grammar[rule][module]:
                grammar[rule].pop(module)

        if not grammar[rule]:
            grammar.pop(rule)
    
    return grammar


def build_expected_tokens(grammar: dict[str, dict]) -> dict:
    """Constructs a dictionary mapping every token to a set of all possible subsequent tokens."""

    def extend_expected_tokens(curr, next) -> list:    
        if not curr in expected_tokens: expected_tokens[curr] = []
        if not next in expected_tokens[curr]: expected_tokens[curr].append(next)

        # Recurse into subsequent grammar rules
        for module in grammar.get(next, []):
            for (variant, pattern) in grammar[next][module]:
                token = pattern[0]
                if (not isinstance(token, str)) and (not token in expected_tokens[curr]):
                    extend_expected_tokens(curr, token)

    expected_tokens: dict[any, list] = {}

    for modules in grammar.values():
        for alternatives in modules.values():
            for pattern in (p for (v, p) in alternatives if p):
                for curr, next in zip(pattern[:-1], pattern[1:]):
                    extend_expected_tokens(curr, next)
                        
    return expected_tokens


def build_expected_patterns(grammar: dict):

    expected_patterns: dict[any, list] = {}

    for rule, modules in grammar.items():
        for module, alternatives in modules.items():
            for (variant, pattern) in alternatives:
                for token in (t for t in pattern if not isinstance(t, str)):
                    if not (token in expected_patterns): expected_patterns[token] = []
                    
                    if not (pattern in expected_patterns[token]):
                        expected_patterns[token].append((rule, module, variant, pattern))

    return expected_patterns


def pathToFunc(path: str) -> str:
    """Converts a path .lib/path/to/somewhere to a function prefix p_path_to_somewhere_<fname>."""
    return f"p_{path.lower().removeprefix(".lib/").replace("/", "_")}_".lower()


def print_warnings(msg: str, log: dict) -> None:
    from datatypes import OrderedSet

    for type, warnings in sorted(log.items(), key=lambda tup: len(tup[0]), reverse=True):
        if warnings:
            print("WARNING: " + msg + f" ({type})")
            for path in OrderedSet(warnings):
                print(f"       | {path}")


def stringify(l: list[object]) -> list[str]:
    return list(map(str, l))



if __name__ == "__main__":
    from sys import argv

    regularize(argv[-1])
