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
        "c", # compile
        "d", # debug
        "t", # test
        "x", # clear
    ]:
        config["flags"][flag] = (f"-{flag}" in argv)
        config["flags"][flag] and args.remove(f"-{flag}")
    
    set_config(config)

    FLAGS = config["flags"]
    

    if FLAGS['x']:
        os.path.exists("AST.py") and os.remove("AST.py")
        os.path.exists("eval.py") and os.remove("eval.py")
        exit()


    args = args[1:]

    if FLAGS['c']: 
        config["paths"]["language"] = os.path.dirname(args.pop())
        config["language"] = config["paths"]["language"].split("/")[-1]
        set_config(config)
        
        compile()
    
    else:
        print(f"Language: {config["language"]}.")


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
 