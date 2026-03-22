"""Customize everything, but nothing more."""



from processing import compile
from utils import get_input

from os.path import abspath, exists
from sys import exit, argv
from time import time
from os import remove



def main(args: list = argv) -> None:
    FLAGS = {
        flag : False for flag in [
            "i", # interactive
            "c", # compile
            "d", # debug
            "t", # test
            "x", # clear
        ]
    }

    for flag in FLAGS:
        FLAGS[flag] = f"-{flag}" in argv
        FLAGS[flag] and args.remove(f"-{flag}")


    if FLAGS['x']:
        exists("AST.py") and remove("AST.py")
        exists("eval.py") and remove("eval.py")
        exit()


    args = args[1:]

    if FLAGS['c']: 
        LANGUAGE = abspath(args.pop(0))
        compile(LANGUAGE)
    
    else:
        from AST import LANGUAGE
    
        print(f"Language: {LANGUAGE.rsplit("/")[-1]}.")


    if FLAGS['t']:
        from tests import test
    
        test(LANGUAGE.rsplit("/")[-1], args)
    
    from eval import process
    
    for arg in args:
        if exists(arg):
            with open(arg) as file:
                process(file.read(), dFlag=FLAGS['d'])

    if FLAGS['i']:
        for line in iter(lambda: get_input("</> "), "quit"):
            if line.strip():
                if FLAGS['d']: start = time()
                process(line, FLAGS['d'])
                if FLAGS['d']: print(f"Runtime: {time() - start}")



if __name__ == "__main__": 
    main()
