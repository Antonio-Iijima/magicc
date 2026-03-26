from processing.syntax import Grammar
from processing.semantics import Eval

from utils import get_config



def compile() -> None:
    dFlag = get_config("flags", "d")

    print(f"Compiling: {get_config("language")}")
    print()

    with open("AST.py", "w") as file:
        grammar = Grammar()
        file.write(grammar.compile())
    
    with open("eval.py", "w") as file:
        file.write(Eval(grammar.dependencies).compile())
    
    if dFlag:
        print()
        print("GRAMMAR")
        print()
        print(grammar)

    print()
    print("Done!")
    print()
