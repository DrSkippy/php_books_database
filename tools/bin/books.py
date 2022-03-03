from code import InteractiveConsole
import bookdbtool.repl_tools as rt

scope_vars = {"BC": rt.BC_Tool()}

header = """Welcome to REPL! We hope you enjoy your stay!\nFor help use help(BC)."""
footer = "Thanks for visiting the REPL today!"

InteractiveConsole(locals=scope_vars).interact(header, footer)