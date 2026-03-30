"""Customize everything, but nothing more."""



from utils import get_input, get_config, set_config
from processing import compile

from sys import exit, argv
from time import time

import os



def main(args: list = argv) -> None:
    config = get_config()
        
    for flag in [
        "i", # interactive
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
    

    set_config(config)
   
   
    args = args[1:]

    if args and os.path.isdir(args[0]):
        config["paths"]["language"] = os.path.dirname(args.pop(0))
        config["language"] = config["paths"]["language"].split("/")[-1]
        print(f"magicc v{config["version"]} </> {config["language"]} {config["implementation"]}")
        set_config(config)
        
        print()

        compile()

    else: print(f"Language: {config["language"]}")


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
