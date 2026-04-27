from utils import pathToFunc



class Rule:
    def __init__(self, children: list, modulename: str = None, variant: int = 0):
        self.__name__ = type(self).__name__
        self.fname = pathToFunc(modulename) + self.__name__.lower()
        self.variant = variant
        self.children = tuple(filter(None, children))
        self.modulename = modulename
        self._hash = self.__name__.__hash__() + sum(child.__hash__() for child in children)


    def depth(self) -> int:
        if (len(self.children) == 1) and isinstance(self.children[0], str): return 1
        return 1 + max(child.depth() for child in self.children)


    def __eq__(self, other: 'Rule'):
        return isinstance(other, Rule) and self.__hash__() == other.__hash__()


    def __hash__(self):
        return self._hash


    def __repr__(self, i=0):
        return \
            "\n" + "   " * i \
            + f"{self.__name__}([{", ".join(repr(child) if isinstance(child, str) else child.__repr__(i+1) for child in self.children)}]," \
            + "\n" + "   " * i \
            +  f"{repr(self.modulename)}, {self.variant})"
            
                
    def __str__(self):
        return self.__name__



class State(list):    
    def __init__(self, iterable = None):
        iterable = iterable or []
        super().__init__(iterable)
        self._hash = sum(token.__hash__() for token in iterable)


    def __hash__(self) -> int:
        return self._hash



class OrderedSet(dict):
    """Implements an ordered set using a `dict`. 
    `add()` and `remove()` methods provide `append()` and `pop()` functionality."""

    def __init__(self, iterable = None):
        super().__init__(dict.fromkeys(iterable) if iterable else {})


    def add(self, item: any) -> None:
        self[item] = None


    def pop(self) -> State:
        """Removes and returns the last value from the `OrderedSet`."""
        return self.popitem()[0]


    def copy(self):
        return OrderedSet(self.keys())
    

    def extend(self, iterable) -> 'OrderedSet':
        for item in iterable:
            self.add(item)

        return self
    
    
    def show(self):
        for item in self:
            print(item)


    def __str__(self) -> str:
        return "{\n" + ",\n".join(f"   {e}" for e in self) + "\n}"
    

    def compile(self):
        return "{\n" + ",\n".join(f"   r'{e}'" for e in sorted(self, key=len, reverse=True)) + "\n}"



class Parsed:
    def __init__(self, sentence: str, AST: Rule, max_states: int):
        self.sentence = sentence
        self.AST = AST
        self.max_states = max_states


    def __str__(self):
        return self.sentence



class Token:
    def __init__(self, tok, line: int, col: int):
        pass
