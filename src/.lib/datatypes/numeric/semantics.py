def p_float(expr):
    return float(expr(0))

def p_int(expr): 
    return int(expr(0))

def p_digit(expr): 
    return int(expr(0))
