from utils import pathToFunc



class Rule:
    def __init__(self, children: list, variant: int = 0, fname: str = None):
        self.__name__ = type(self).__name__
        self.fname = fname
        self.variant = variant
        self._str = " ".join(map(str, children))
        self.children = tuple(c for c in children if c)
        self._hash = self.__name__.__hash__() + sum(child.__hash__() for child in children)


    def tree(self, level: int = 0, space: str = "   "):
        print(space*level + f" ({level}) " + self.__name__)
        for c in self.children:
            if isinstance(c, Rule):
                c.tree(level+1)
            else:
                print(space*(level+1) + f" ({level+1}) " + c)


    def __eq__(self, other: 'Rule'):
        return isinstance(other, Rule) and self.__hash__() == other.__hash__()


    def __hash__(self):
        return self._hash


    def __repr__(self):
        return self.__name__
            
                
    def __str__(self):
        return self._str



class GrammarRule:
    def __init__(self, rule: Rule, module: str):
        self.rule = rule
        self.name = rule.__name__
        self.module = module
        self.fname = pathToFunc(self.module) + self.name.lower()

    
    def __call__(self, *args, **kwargs) -> Rule:
        return self.rule(*args, **kwargs, fname=self.fname)
    

    def __hash__(self):
        return self.fname.__hash__()
    
    
    def __eq__(self, other):
        if not isinstance(other, (GrammarRule, Rule, str)):
            return False
        
        return (other if isinstance(other, str) else other.fname) == self.fname


    def __str__(self):
        return f"<{self.name}>"
    

    def __repr__(self):
        return str(self)



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


    def add(self, item, overwrite: bool = False):
        if overwrite: self.pop(item, None)
        self[item] = None


    def remove(self) -> State:
        return self.popitem()[0]


    def copy(self):
        return OrderedSet(self.keys())
    

    def extend(self, iterable, overwrite: bool = False) -> 'OrderedSet':
        for item in iterable:
            self.add(item, overwrite)

        return self
    
    
    def show(self):
        for item in self:
            print(item)


    def __str__(self) -> str:
        return "{\n" + ",\n".join(f"   {e}" for e in self) + "\n}"
    

    def compile(self):
        return "{\n" + ",\n".join(f"   r'{e}'" for e in sorted(self, key=len, reverse=True)) + "\n}"



class Parsed:
    def __init__(self, sentence: str, AST: Rule, max_states: int, showTree: bool = False):
        self.sentence = sentence
        self.AST = AST
        self.max_states = max_states
        if showTree: print(AST.tree())


    def get(self):
        return self.AST


    def __str__(self):
        return self.sentence
