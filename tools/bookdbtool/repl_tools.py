import logging

import requests


class REPL_Tool:
    ENDPOINT = "http://192.168.127.8/books"
    PAGE_SIZE = 20

    def __init__(self):
        pass

    def help(self, ref):
        """List available functions for accessing book collection database."""
        for x in dir(ref):
            if not x.startswith("_"):
                print("-"*40)
                print(x)
                print("-"*40)
                print(exec(f"ref.{x}.__doc__"))


    def _reduce_string(self, row, idxs):
        return [row[i] for i in idxs]


    def _print_rows(self, data, header, indexes, format_string):
        if len(data) == 0:
            print("No data")
        else:
            hs = format_string.replace("d", "s").format(*self._reduce_string(header, indexes))
            print(hs)
            print("-"*len(hs))
            for i, row in enumerate(data):
                print(format_string.format(*self._reduce_string(row, indexes)))
                if i % self.PAGE_SIZE == self.PAGE_SIZE - 1:
                    a = input("<return> to cont, q to quit...")
                    if a.lower().startswith("q"):
                        break
        return


    def tag_counts(self, tag=None):
        """ Takes 0 or 1 arguments. If an argument is provided, only tags matching this root string will appear. """
        q = self.ENDPOINT + "/tag_counts"
        if tag is not None:
            q += f"/{tag}"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            fmt = "{:25s}: {:8d}"
            self._print_rows(res["data"], res["header"], [0, 1], fmt)

    def books(self, **query):
        """ Takes 0 or many arguments. E.g. Title="two citites", Author="Dickens" """
        q = self.ENDPOINT + "/books?"
        first = True
        for k, v in query.items():
            if first:
                first = False
            else:
                q += "&"
            q += f"{k}={v}"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            fmt = "{:12d} | {:75s}\n             | {:25s}"
            self._print_rows(res["data"], res["header"], [0, 1, 2], fmt)


if __name__ == "__main__":
    rpl = REPL_Tool()
    rpl.tag_counts()
    rpl.books(Title="science")
