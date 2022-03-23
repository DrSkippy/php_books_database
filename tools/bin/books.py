from code import InteractiveConsole
import bookdbtool.repl_tools as rt
import readline

scope_vars = {"bc": rt.BC_Tool()}

header = """Welcome to the Book Collection Database REPL!\nWe hope you enjoy your stay!\nFor help use help(bc)."""
footer = "Thanks for visiting the REPL today!"

InteractiveConsole(locals=scope_vars).interact(header, footer)