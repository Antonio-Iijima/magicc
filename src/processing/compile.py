from processing.syntax import Grammar
from processing.semantics import Eval



def compile(path: str) -> None:

    print(f"Compiling: {path.rsplit("/")[-1]}")
    print()

    with open("AST.py", "w") as file:
        grammar = Grammar(path)
        file.write(grammar.compile())
    
    with open("eval.py", "w") as file:
        file.write(Eval(path, grammar.dependencies).compile())
    
    # print()
    # print("GRAMMAR")
    # print()
    # print(grammar)

    print()
    print("Done!")
    print()



if __name__ == "__main__":
    test = Grammar("languages/banter")
    # print(test)
    # print(test.compile())
    ev = Eval(test.path, test.dependencies)
    print(ev.compile())
