import logging

import requests
from columnar import columnar


class BC_Tool:
    ENDPOINT = "http://192.168.127.8/books"
    PAGE_SIZE = 20
    MINIMAL_BOOK_INDEXES = [0, 1, 2, 6, 7, 8]

    def __init__(self):
        pass

    def _row_column_selector(self, row, indexes):
        return [row[i] for i in indexes]

    def _column_selector(self, data, indexes):
        return [self._row_column_selector(i, indexes) for i in data]

    def _show_table(self, data, header, indexes):
        table = columnar(self._column_selector(data, indexes), self._row_column_selector(header, indexes))
        print(table)

    def version(self):
        """ Retrieve the back end version. """
        q = self.ENDPOINT + "/configuration"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            print("Version: {}".format(res["version"]))

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
            self._show_table(res["data"], res["header"], [0, 1])

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
            self._show_table(res["data"], res["header"], self.MINIMAL_BOOK_INDEXES)

    def book(self, book_collection_id):
        """ Takes 1 argument."""
        q = self.ENDPOINT + f"/books?BookCollectionID={book_collection_id}"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            q = self.ENDPOINT + f"/tags/{book_collection_id}"
            try:
                tr = requests.get(q)
                tres = tr.json()
            except requests.RequestException as e:
                logging.error(e)
            else:
                _template = ["" for i in range(len(res["data"][0]))]
                _template[0] = "    Tags:"
                _data = []
                for d in res["data"]:
                    _data.append(d)
                    if len(tres["tag_list"]) > 0:
                        _template[1] = "\n".join(tres["tag_list"])
                        _data.append(_template)
                self._show_table(_data, res["header"], self.MINIMAL_BOOK_INDEXES)

    def books_read_by_year(self, year=None):
        """ Takes 1 argument."""
        q = self.ENDPOINT + "/books_read_by_year"
        if year is not None:
            q += f"/{year}"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            _data = []
            for year, pages, books in res["data"]:
                q = self.ENDPOINT + f"/books?LastRead={year}"
                try:
                    tr = requests.get(q)
                    tres = tr.json()
                except requests.RequestException as e:
                    logging.error(e)
                else:
                    _data.extend(tres["data"])
                    _template = ["" for i in range(len(tres["data"][0]))]
                    _template[0] = f" **** {year} ****"
                    _template[1] = f"Books = {books}"
                    _template[2] = f"Pages = {pages}"
                    _data.append(_template)
            self._show_table(_data, tres["header"], self.MINIMAL_BOOK_INDEXES)


if __name__ == "__main__":
    rpl = REPL_Tool()
    rpl.tag_counts()
    rpl.books(Title="science")
