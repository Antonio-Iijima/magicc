def p_program(expr):
    for i in range(len(expr)-1):
        print(expr(i))
    return expr(-1)
