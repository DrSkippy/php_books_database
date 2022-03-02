from code import InteractiveConsole
import bookdbtool.repl_tools as rt

scope_vars = {"col": rt.REPL_Tool()}

header = "Welcome to REPL! We hope you enjoy your stay!"
footer = "Thanks for visiting the REPL today!"

InteractiveConsole(locals=scope_vars).interact(header, footer)