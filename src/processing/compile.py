from processing.syntax import Grammar
from processing.semantics import Eval

from utils import config



def compile(path: str) -> None:
    dFlag = config("flags", "d")

    print(f"Compiling: {path.rsplit("/")[-1]}")
    print()

    with open("AST.py", "w") as file:
        grammar = Grammar(path)
        file.write(grammar.compile())
    
    with open("eval.py", "w") as file:
        file.write(Eval(path, grammar.dependencies, grammar.MAIN).compile())
    
    if dFlag:
        print()
        print("GRAMMAR")
        print()
        print(grammar)

    print()
    print("Done!")
    print()



if __name__ == "__main__":
    test = Grammar("languages/banter")
    # print(test)
    # print(test.compile())
    ev = Eval(test.path, test.dependencies)
    print(ev.compile())
