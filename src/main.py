from utils import get_config, set_config, get_input

import processing.compile

import click, os

from time import time



@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli(): pass



@cli.command
@click.argument("path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("-i", "--interpreter", "option", flag_value="interpreter", help="Compile an interpreter.", default=True)
@click.option("-c", "--compiler", "option", flag_value="compiler", help="Compile a compiler.")
def compile(path: str, option: bool):
    """Compiles a language system from the files provided in PATH."""

    cfg = get_config()

    cfg["paths"]["language"] = "/".join(path.split("/")[-2:])
    cfg["language"] = path.split("/")[-1]
    cfg["implementation"] = option

    set_config(cfg)

    processing.compile.compile()



@cli.command
@click.argument("input", nargs=-1)
@click.option("-o", "--output", default=get_config("output"), help="Name for output file (only necessary when compiling).", show_default=True)
@click.option("-f", "--force", is_flag=True, help="Force recompilation.")
@click.option("-i", "--interactive", is_flag=True, help="Run in interative mode.")
@click.option("-d", "--debug", is_flag=True, help="Run in debug mode.")
@click.option("-x", "--clear", is_flag=True, help="Delete cached compiled files.")
def run(input, **flags):
    """Runs a compiled language with OPTIONS."""

    cfg = get_config()

    cfg["input"] = input
    cfg["output"] = flags.pop("output")
    cfg["flags"] = flags

    isModified = not (cfg == get_config())

    set_config(cfg)

    if cfg["flags"]["force"] or isModified:
        processing.compile.compile()


    print(f"magicc v{cfg["version"]} </> {cfg["language"]} {cfg["implementation"]}")


    if cfg["flags"]["clear"]:
        os.path.exists("AST.py") and os.remove("AST.py")
        os.path.exists("eval.py") and os.remove("eval.py")

    
    from eval import process


    for filename in input:
        with open(filename) as file:
            process(file.read())

    if cfg["flags"]["interactive"]:
        for line in iter(lambda: get_input("</> "), "quit"):
            if line.strip():
                if cfg["flags"]["debug"]: start = time()
                process(line)
                if cfg["flags"]["debug"]: print(f"Runtime: {time() - start}")    



@cli.command
@click.argument("tests", type=int, nargs=-1)
def test(tests):
    """Run specified built-in test cases."""
    
    if get_config("implementation") == "compiler":
        print("No test cases for compiled languages.")
        return


    from tests import test

    cfg = get_config()
    
    cfg["tests"] = tests
    
    set_config(cfg)

    test(tests)



if __name__ == "__main__":
    cli()
