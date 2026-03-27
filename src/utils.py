from io import TextIOWrapper
from json import load, dump

import re
import os



def get_config(*keys): 
    """Look up a value from the config, applying keys sequentially.
    No arguments returns the config itself."""
    
    cfg = load(open(os.path.join(os.path.dirname(__file__), "config.json")))
    for key in keys:
        if key:
            cfg = cfg[key]
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
        print(f"Language: {get_config("language")}")
        return ""
    
    elif s.endswith("\n"):
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


def build_expected_tokens(grammar: dict[str, dict], nulls: set) -> dict:
    """Constructs a dictionary mapping every token to a set of all possible subsequent tokens."""

    def extend_expected_tokens(curr, next) -> list:    
        if not curr in expected_tokens: expected_tokens[curr] = []
        if not next in expected_tokens[curr]: expected_tokens[curr].append(next)

        # Recurse into subsequent grammar rules
        for module in grammar.get(next, []):
            for pattern in grammar[next][module]:
                token = pattern[0]
                if (not isinstance(token, str)) and (not token in expected_tokens[curr]):
                    extend_expected_tokens(curr, token)

    expected_tokens: dict[any, list] = {}

    for modules in grammar.values():
        for alternatives in modules.values():
            for pattern in (p for p in alternatives if len(p) > 1):
                for curr, next in zip(pattern[:-1], pattern[1:]):
                    extend_expected_tokens(curr, next)
                        
    return expected_tokens


def build_expected_patterns(grammar: dict):

    expected_patterns: dict[any, list] = {}

    for rule, modules in grammar.items():
        for module, alternatives in modules.items():
            for variant, pattern in enumerate(alternatives):
                for token in (t for t in pattern if not isinstance(t, (str, int))):
                    if not (token in expected_patterns): expected_patterns[token] = []
                    
                    if not (pattern in expected_patterns[token]):
                        expected_patterns[token].append((rule, module, variant, pattern))

    return expected_patterns


def pathToFunc(path: str) -> str:
    """Converts a path .lib/path/to/somewhere to a function prefix p_path_to_somewhere_<fname>."""
    return f"p_{path.lower().removeprefix(".lib/").replace("/", "_")}_".lower()


def print_warning(msg: str, log: dict) -> None:
    from datatypes import OrderedSet

    if log["dependency"] or log["main"]:
        print("WARNING: " + msg)
        for path in OrderedSet(log["dependency"]):
            print(f"       | {path}")

        if log["main"]:
            print(f"       | {log["main"][0]}")



if __name__ == "__main__":
    from sys import argv

    regularize(argv[-1] + "/syntax.txt")
