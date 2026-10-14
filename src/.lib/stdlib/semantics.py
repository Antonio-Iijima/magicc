def p_newline(expr): pass


def p_atoms_0(expr):
    return ()

def p_atoms_1(expr):
    return (expr(0), *expr(1))
