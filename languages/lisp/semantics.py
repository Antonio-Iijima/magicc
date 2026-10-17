### META-PROCEDURES ###


def fname(name: str) -> str:
    return f"{
        name
            .removeprefix("f_")
            .removeprefix("q_")
    }{"?"*name.startswith("q_")}"


def applicative(func):
    def wrapper(*args):
        return func(*map(evaluate, args))

    wrapper.__qualname__ = fname(func.__name__)
    
    return wrapper


### PROCEDURES ###


@applicative
def f_add(a, b):
    return a + b

@applicative
def f_sub(a, b):
    return a - b

@applicative
def f_mult(a, b):
    return a * b

@applicative
def f_fdiv(a, b):
    return a / b

@applicative
def f_idiv(a, b):
    return a // b

@applicative
def f_exp(a, b):
    return a ** b

@applicative
def f_mod(a, b):
    return a % b

@applicative
def f_le(a, b):
    return a < b

@applicative
def f_leq(a, b):
    return a <= b

@applicative
def f_ge(a, b):
    return a > b

@applicative
def f_geq(a, b):
    return a >= b

@applicative
def f_eq(a, b):
    return a == b

@applicative
def f_list(*a):
    return list(a)

def f_and(a, b):
    return evaluate(a) and evaluate(b)

def f_or(a, b):
    return evaluate(a) or evaluate(b)

def f_not(a):
    return not evaluate(a)

# predicates

@applicative
def q_eq(a, b):
    return a == b

@applicative
def q_atom(a):
    return isatom(a)

@applicative
def q_list(a):
    return islist(a)

@applicative
def q_null(a):
    return isnull(a)

@applicative
def q_bool(a):
    return isinstance(a, bool)

# more procedures

def cxr(x: str):

    @applicative
    def f_cxr(a) -> any:
        nonlocal x
        while x:
            x, c = x[:-1], x[-1]
            match c:
                case "a": a = a[0]
                case "d": a = a[1:]
        return a

    return f_cxr

def f_quote(x):
    return x

@applicative
def f_cons(a, b):
    return [a] + b

@applicative
def f_eval(x):
    return evaluate(x)

def f_lambda(params, body):
    
    @applicative
    def λ(*args):
        g_env.append({ param : arg for param, arg in zip(params, args) })
        value = evaluate(body)
        g_env.pop()
        return value
    
    return λ

def f_define(name, body):
    g_env[-1][name] = evaluate(body)

def f_defun(name, params, body):
    g_env[-1][name] = f_lambda(params, body)

def f_ternary(a, b, c):
    return evaluate(b) if evaluate(a) else evaluate(c)

def f_cond(*options):
    for (condition, body) in options:
        if condition == "else" or evaluate(condition): return evaluate(body)

def f_let(bindings, body):
    params, args = zip(*bindings)
    return f_lambda(params, body)(*args)

def f_letstar(bindings, body):
    if bindings == []: return evaluate(body)
    param, arg = bindings[0]
    return f_lambda(param, ["let*", bindings[1:], body])(arg)

def f_letrec(bindings, body):
    params, _ = zip(*bindings)
    g_env.append(dict.fromkeys(params, LookupError))
    for param, arg in bindings:
        g_env[-1][param] = evaluate(arg)
    value = evaluate(body)
    g_env.pop()
    return value


### ENVIRONMENT & BUILTINS ###


g_aliases = {
    "+" : "add",
    "-" : "sub",
    "*" : "mult",
    "/" : "fdiv",
    "//" : "idiv",
    "**" : "exp",
    "%" : "mod",
    "?" : "ternary",
    "<" : "le",
    "<=" : "leq",
    ">" : "ge",
    ">=" : "geq",
    "==" : "eq",
    "let*" : "letstar",
}

g_env = [{}]

# normal procedures
g_env[0].update({
    fname(name) : procedure for name, procedure in globals().items() if name.startswith("f_") 
})

# predicates
g_env[0].update({
    fname(name) : predicate for name, predicate in globals().items() if name.startswith("q_")
})


### OUTPUT ###


def toLisp(s: list|str) -> str:
    return f"({" ".join((toLisp(e) for e in s))})" if isinstance(s, list) else str(s)


### SEMANTICS ###


def p_program_0(expr):
    value = evaluate(expr(0))
    if value is not None: print(toLisp(value))

def p_program_1(expr):
    p_program_0(expr)
    expr(1)


def p_lisp_expr_0(expr):
    return ["quote", expr(1)]


def p_list_0(expr):
    return []

def p_list_1(expr):
    return list(expr(1))


def p_elems_0(expr):
    return (expr(0), )

def p_elems_1(expr):
    return (expr(0), *expr(1))


### INTERPRETER ###


def isatom(expr): return not isinstance(expr, list)

def islist(expr): return isinstance(expr, list)

def isnull(expr): return expr == []

def isliteral(expr): return isinstance(expr, (int, float, bool))


def lookup(var):
    from re import fullmatch

    # follow operator aliases (e.g. + : "add")
    var = g_aliases.get(var, var)

    # prioritize car/cdr operators
    if fullmatch(r"c[ad]+r", var):
        return cxr(var[1:-1])

    # try to find declared or builtin values / procedures
    for scope in reversed(g_env):
        val = scope.get(var, LookupError)
        if not (val == LookupError):
            return val

    # otherwise not found
    raise NameError(f"variable {var} not found.")


def evaluate(expr):

    if isatom(expr):
        
        # literals evaluate to themselves
        if isliteral(expr): return expr
        
        # lookup everything else in the environment
        return lookup(expr)

    # lists are treated as function applications by default
    elif islist(expr):

        # empty list evaluates to itself
        if isnull(expr): return expr
        
        # Evaluate operators/builtins
        return evaluate(expr[0])(*expr[1:])
