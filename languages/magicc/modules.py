from config import CONFIG


import functools
import shutil
import os



def flip(s: str, c: str) -> str:
    return s.translate({ ord(e) : c for e in {".", "/", "_"}.difference({c}) })


def transform_semantics(filename: str, modulename: str) -> str:
    from re import Match
    from re import sub

    def replace_fname(match: Match) -> str:
        return f"p_{modulename}_{match.group().removeprefix("p_")}".lower()

    with open(filename) as file:
        return sub(
            pattern=r"p_\w*\(",
            repl=replace_fname,
            string=file.read()
        )



class Path:
    def __init__(self, path: str):
        self.path = path

    @property
    @functools.cache
    def asModule(self) -> str:
        return flip(self.path, "_").upper()

    @property
    @functools.cache
    def asPath(self) -> str:
        return flip(self.path, "/").upper()

    @property
    @functools.cache
    def asRequirement(self) -> str:
        return flip(self.path, ".").upper()

"""
Module needs to produce:

GRAMMAR: dict[Nonterminal, list[Production]] = {
    START() : [ Production(START(), MAIN, 0, [Nonterminal("PROGRAM"), EOI()]) ]
}

dict[
    Nonterminal, 
    list[
        Production(
            Nonterminal(rule), 
            str(Module), 
            int(variant), 
            list(pattern)
        )
    ]
]

TERMINALS: set[Terminal] = set()
"""


class Module:
    
    parse: callable = None

    indentation: bool = False
    newlines: bool = False

    # track to catch circular requirements
    paths: set = set()
    
    grammar: dict = {}
    terminals: set = set()

    def __init__(self, path: str):
        self.path = path
        self.contents = {}

        process = "compiler" if CONFIG.flags.metacompile else "parser"
        paths = []
        modules = []

        for filename in os.listdir(path):
            # process syntax file into { 0: ..., 1: ..., 2: ...}
            if os.path.isfile(filename) and filename.endswith("syntax.txt"):
                with open(filename) as file:
                    self.contents = self.parse(file.read())(0)

            # transform/copy over all other (semantics) files
            else:
                with open(os.path.join(
                    CONFIG.paths.root, 
                    process, 
                    os.path.basename(filename))
                    ) as file:
                    file.write(transform_semantics(filename))


    def setup(self):
        paths = []
        modules = []

        process = "compiler" if CONFIG.flags.metacompile else "parser"

        for n, data in self.contents.items():
            match n:
                case 0: 
                    if data in Module.paths:
                        raise CircularRequirement(self.name)
                    Module.paths.add(data)
                    paths.append(Module(data))
                case 1:
                    param, arg = data
                    if not param in Module.definitions:
                        Module.definitions[param] = arg
                case 2:
                    grammar: dict[str, list] = { rule : alternatives for rule, alternatives in data }

        while paths:
            path = paths.pop()
            for filename in os.listdir(path):
                if filename.endswith("syntax.txt"):
                    with open(filename) as file:
                        module: Module = self.parse(file.read())()
                        modules.append(module.set_name(path))

                elif filename.endswith(".py"):
                    with open(os.path.join(CONFIG.paths.root, process, filename.rsplit("/")[-1])) as file:
                        file.write(transform_semantics(filename))

                # add support for nested directories

        for module in modules:
            for rule, alternatives in module.contents.items():
                for variant, pattern in alternatives:
                    rule.append((rule, module.name, variant, pattern))

        

                                    




class CircularRequirement(Exception):pass