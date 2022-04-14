import readline
from code import InteractiveConsole

import bookdbtool.repl_tools as rt


def history():
    print("-" * 50)
    print('\n'.join([str(readline.get_history_item(i + 1)) for i in range(readline.get_current_history_length())]))
    print("-" * 50)


scope_vars = {"bc": rt.BC_Tool(), "history": history}

header = """Welcome to the Book Collection Database REPL!\nWe hope you enjoy your stay!\nFor help use help(bc)."""
footer = "Thanks for visiting the REPL today!"

InteractiveConsole(locals=scope_vars).interact(header, footer)
