g_vars = {}



def p_program_1(expr):
    print(expr(0))
    return expr(2)


def p_boolexpr(expr):
    expr(1)
    return expr(3)


def p_declarations_1(expr):
    expr(1)


def p_varlist_0(expr):
    g_vars[expr(0)] = True

def p_varlist_1(expr):
    g_vars[expr(0)] = True
    expr(2)


def p_expr_0(expr):
    return expr(0) and expr(2)

def p_expr_1(expr):
    return expr(0) or expr(2)

def p_expr_2(expr):
    return not expr(1)

def p_expr_3(expr):
    return expr(0) == 't'

def p_expr_4(expr):
    return g_vars.get(expr(0), False)
