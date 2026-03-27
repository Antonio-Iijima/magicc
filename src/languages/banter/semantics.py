g_env = {}
g_markers = {}



def p_statement_list_1(expr):
    expr(0)
    expr(2)


def p_label(expr):
    try:
        return g_env[expr(0)]
    except KeyError:
        raise Exception(1, f"Error: variable {expr(0)} not declared.")

def p_bool(expr):
    return expr(0) == "True"


def p_assignment(expr):
    g_env[expr(1)] = expr(3)


def p_if_then(expr):
    if expr(1): 
        expr(4)

def p_if_then_else(expr):
    if expr(1):
        expr(4)
    else: 
        expr(7)

def p_block(expr):
    return expr(2)


def p_return(expr):
    raise Exception(0, expr(1))


def p_marker(expr):
    mark = expr(1)
    jump = True
    while jump:
        try:
            expr(3)
            jump = False
        except Exception as e:
            jump = (e.args == (2, mark))
            if not jump: 
                if len(e.args) > 0 and e.args[0] == 2:
                    print(f"ERROR: cannot reference marker '{e.args[1]}' before declaration")
                e.args = (1, e.args[1])
                raise e

def p_jump(expr):
    raise Exception(2, expr(2))


def p_print(expr):
    print(expr(1))
