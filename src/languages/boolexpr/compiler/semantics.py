g_env = set()



def p_program(expr):
    print(f"Compiling {expr} to C++")
    return expr(0)


def p_boolexpr(expr):
    global g_env

    g_env = set(expr(1))

    return f"""#include <iostream>

using namespace std;

int main() {{
    {"\n   ".join(f"bool {var} = {"true" if var in g_env else "false"}" for var in expr(1))}

    bool result = {expr(3)};

    cout << "   The result is ";

    if (result)
        cout << "true";
    else
        cout << "false";

    cout << "." << endl;
}}
"""


def p_expr_0(expr):
    return f"{expr(0)} || {expr(2)}"

def p_and_0(expr):
    return f"{expr(0)} && {expr(2)}"

def p_not_0(expr):
    return f"! {expr(1)}"


def p_literal(expr):
    return "true" if expr(0) == 't' else "false"

def p_var(expr):
    var = expr(0)
    return var if var in g_env else "false"
