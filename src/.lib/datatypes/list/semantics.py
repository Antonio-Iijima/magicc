def p_empty_list(expr):
    return []

def p_lat(expr):
    return [ *expr(0) ]

def p_lat_1(expr):
    return expr(0), *expr(1)

def p_atoms(expr):
    return expr(1)
