from processing.syntax import Grammar
from processing.semantics import Eval

from utils import get_config



def compile() -> None:

    if get_config("lock"): return None
    
    print()
    print(f"Compiling...")
    print()

    with open("AST.py", "w") as file:
        grammar = Grammar()
        file.write(grammar.compile())
    
    with open("eval.py", "w") as file:
        file.write(Eval(grammar.dependencies).compile())

    if get_config("flags", "debug"):
        print()
        print("GRAMMAR")
        print()
        print(grammar)

    print()
    print("Done!")
    print()
