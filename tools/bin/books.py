import json
import readline
from code import InteractiveConsole

import bookdbtool.estimate_tools as et
import bookdbtool.repl_tools as rt
import bookdbtool.isbn_lookup as isbn
import bookdbtool.ai_tools as ai

CONFIG_PATH = "/book_service/config/configuration.json"  # root is "tools"


def get_endpoint():
    try:
        cfile = open(f".{CONFIG_PATH}", "r")
    except OSError:
        try:
            cfile = open(f"..{CONFIG_PATH}", "r")
        except OSError:
            print("Configuration file not found!")
    with cfile:
        config = json.load(cfile)
        end_point = config["endpoint"]
        api_key = config["api_key"]
        # todo fix this so everyone uses the same config
    return config, (end_point, api_key), config["isbn_com"]


ai_conf, book_service_conf, isbn_conf = get_endpoint()


def history():
    print("-" * 50)
    print('\n'.join([str(readline.get_history_item(i + 1)) for i in range(readline.get_current_history_length())]))
    print("-" * 50)


scope_vars = {"bc": rt.BCTool(*book_service_conf),
              "est": et.ESTTool(*book_service_conf),
              "isbn": isbn.ISBNLookup(isbn_conf),
              "ai": ai.OllamaAgent(ai_conf),
              "history": history}

header = "************************************************************************\n"
header += "** Welcome to the Book Collection Database REPL!                      **\n"
header += "** For help, please use help(bc). help(isbn),                         **\n"
header += "**     help(ai), and help(est).                                       **\n"
header += "** Use exit() to leave the REPL.                                      **\n"
header += "** Use history() to see the command history. Up arrow for previous.   **\n"
header += "************************************************************************\n"
footer = "Thanks for visiting the Book Collection REPL today!"

InteractiveConsole(locals=scope_vars).interact(header, footer)
