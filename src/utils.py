from io import TextIOWrapper

import re



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


if __name__ == "__main__":
    from sys import argv

    regularize(argv[-1] + "/syntax.txt")