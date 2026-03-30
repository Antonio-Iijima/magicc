def p_program(expr):
    return f"""# Banter -> Python
    
    
{expr(0).strip()}
"""


def p_statement_list_1(expr):
    return f"""
{expr(0)}
{expr(2)}
"""


def p_assignment(expr):
    return f"{expr(1)} = {expr(3)}"


def p_if_then(expr):
    return f"""
if {expr(1)}:
{expr(4)}
"""


def p_if_then_else(expr):
   return f"""
if {expr(1)}:
{expr(4)}
else:
{expr(7)}
""" 


def p_block(expr):
    block = str(expr(2))
    return indent(block)

def indent(text):
    return "   " + text.replace("\n", "\n   ")


def p_return(expr):
    return f"""
print({expr(1)})
quit()
"""


def p_until(expr):
    return f"""
while (not {expr(1)}):
{expr(3)}
"""


def p_print(expr):
    return f"print({expr(1)})"
