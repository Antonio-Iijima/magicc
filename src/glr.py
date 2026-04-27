from AST import *
from rich import print



class GLR:
    table = {}
    tokens = []
    current = None
    next = None


    def __init__(self):
        """A dictionary: `table[current][next] = [(ACTION, *data)+]`"""
        self.generate_table()


    def generate_table(self) -> dict:

        for rule, modules in GRAMMAR.items():
            if not rule.__name__ in self.table:
                self.table[rule.__name__] = {}

            for module, alternatives in modules.items():
                for (variant, pattern) in alternatives:
                    for (current, next) in zip(pattern, pattern[1:] + [None]):
                        curr_name = current if isinstance(current, str) else current.__name__
                        nxt_name = next if isinstance(next, (str, type(None))) else next.__name__

                        if not curr_name in self.table:
                            self.table[curr_name] = {}

                        # what do we do given a state (rule), current token, and next token.
                        # if possibilities already exist, add to them. 
                        actions = self.table[curr_name].get(nxt_name, [])

                        # for the last token, we reduce
                        if next is None:
                            actions.append(("REDUCE", (rule, module, variant, pattern)))

                        else:
                        # we shift if the next token will require no processing (i.e. is a terminal in the grammar),
                        # otherwise we jump to the state for that token (nonterminal).
                            actions.append(("GOTO", next))

                        self.table[curr_name][nxt_name] = actions

        return self.table


    def parse(self, tokens: list):
        
        print(stringify(tokens))
        print(GLR.table)
        GLR.tokens = tokens
        stack, current, next = shift([])
        return parse(stack, current, next)



def parse(stack: list = None, current = None, next = None) -> PROGRAM|None:
    stack = stack or []

    if len(stack) == 1 and isinstance(stack[0], PROGRAM):
        return stack[0]

    # Start by shifting a token

    actions = GLR.table[current].get(next, GLR.table[current].get(None, []))

    print(f"""
stack   : {stringify(stack)}
tokens  : {stringify(GLR.tokens)}
current : {current}
next    : {next}
action  : {actions}
""")
    
    if actions:
        return do_actions(stack, actions, current)
    else:
        stack, current, next = shift(stack)

    return parse(stack, current, next)



def do_actions(stack, actions: list, current) -> PROGRAM|None:
    if not actions: 
        return None
    
    stack = stack[:]

    action, data = actions.pop()

    out = None

    match action:
        case "REDUCE":
            (rule, module, variant, pattern) = data
            idx = len(stack) - len(pattern)
            reducible = stack[idx:]

            if (list(map(type, reducible)) == pattern):
                out = parse(stack[:idx] + [rule(reducible, module, variant)], current)
        
        case "GOTO":
            out = parse(stack, data.__name__, next)

    return out or do_actions(stack, actions, current)


def shift(stack):
    print("SHIFT")

    stack.append(GLR.tokens.pop(0))

    current = stack[-1].__name__

    next = type(GLR.tokens[0]).__name__ if GLR.tokens else None

    return stack, current, next