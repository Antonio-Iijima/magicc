"""Customize everything, but nothing more."""



from utils import get_input, get_config, set_config
from processing.compile import compile

from sys import exit, argv
from time import time

import os



def main(args: list = argv[1:]) -> None:
    """How to use the CLI:

magicc aims to abstract as much as possible. 
To this end, the config is saved at the end of each run,
and values are only changed when provided.
This means that, for instance, if you provide the `--c` flag and a directory in order to compile,
future runs will use the generated compiler files for that language unless otherwise specified.
    
    
"""
    config = get_config()
        
    for flag in [
        "f", # force compile
        "i", # interpreter
        "d", # debug
        "t", # test
        "x", # clear
    ]:
        config["flags"][flag] = (f"-{flag}" in args)
        config["flags"][flag] and args.remove(f"-{flag}")
        
    FLAGS = config["flags"]


    if FLAGS['x']:
        os.path.exists("AST.py") and os.remove("AST.py")
        os.path.exists("eval.py") and os.remove("eval.py")
        exit()


    if "--i" in args: 
        config["implementation"] = "interpreter"
        args.remove("--i")
    elif "--c" in args: 
        config["implementation"] = "compiler"
        args.remove("--c")


    if config["implementation"] == "compiler":
        if len(args) == 2:
            config["output"] = args.pop()
        elif len(args) > 2:
            print(f"ERROR: irregular number of file arguments for compiler (received {len(args)}, expected 2). Please specify exactly one input and one output.")
            quit()


    if args and os.path.isdir(args[0]):
        config["paths"]["language"] = os.path.dirname(args.pop(0))
        config["language"] = config["paths"]["language"].split("/")[-1]

    print(f"magicc v{config["version"]} </> {config["language"]} {config["implementation"]}")

    if FLAGS['f'] or not (config == get_config()):
        set_config(config)
        print()
        compile()


    if FLAGS['t']:
        from tests import test
    
        test(args)
    
    
    from eval import process


    for arg in args:
        if os.path.exists(arg):
            with open(arg) as file:
                process(file.read())

    if FLAGS['i']:
        for line in iter(lambda: get_input("</> "), "quit"):
            if line.strip():
                if FLAGS['d']: start = time()
                process(line)
                if FLAGS['d']: print(f"Runtime: {time() - start}")



if __name__ == "__main__": 
    main()
