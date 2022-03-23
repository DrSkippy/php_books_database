import datetime
import logging

import pandas as pd
import requests
from columnar import columnar


class BC_Tool:
    ENDPOINT = "http://192.168.127.8/books"
    # ENDPOINT = "http://172.17.0.2:8083"
    PAGE_SIZE = 20
    COLUMN_INDEX = {
        "BookCollectionID": 0,
        "Title": 1,
        "Author": 2,
        "CopyrightDate": 3,
        "ISBNNumber": 4,
        "PublisherName": 5,
        "CoverType": 6,
        "Pages": 7,
        "Category": 8,
        "Note": 19,
        "Location": 11,
        "ISBNNumber13": 12,
        "ReadDate": 13
    }
    MINIMAL_BOOK_INDEXES = [0, 1, 2, 7, 9, 10, 11, 13]

    def __init__(self):
        self.result = None

    def _row_column_selector(self, row, indexes):
        return [row[i] for i in indexes]

    def _column_selector(self, data, indexes):
        return [self._row_column_selector(i, indexes) for i in data]

    def _show_table(self, data, header, indexes):
        try:
            table = columnar(self._column_selector(data, indexes), self._row_column_selector(header, indexes))
            print(table)
        except TypeError as e:
            print("No data")

    def _populate_new_book_record(self):
        proto = {
            "Title": "",
            "Author": "",
            "CopyrightDate": "",
            "ISBNNumber": "",
            "ISBNNumber13": "",
            "PublisherName": "",
            "CoverType": "Digital, Hard, Soft",
            "Pages": 0,
            "Location": "Main Collection, DOWNLOAD, Oversized, Pets, Woodwork, Reference, Birding",
            "Note": "",
            "Recycled": "0=No or 1=Yes"
        }
        return self._inputer(proto)

    def _populate_update_read_dates(self, id, today=True):
        proto = {
            "BookCollectionID": id,
            "ReadDate": datetime.date.today().strftime("%Y-%m-%d"),
            "ReadNote": ""
        }
        return self._inputer(proto, exclude_keys=["BookCollectionID", "ReadDate"])

    def _inputer(self, proto, exclude_keys=[]):
        for key in proto:
            if key in exclude_keys:
                print(f"{key}: {proto[key]}")
            else:
                a = input(f"{key} ({proto[key]}): ")
                proto[key] = a
        return proto

    def version(self):
        """ Retrieve the back end version. """
        q = self.ENDPOINT + "/configuration"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            print("Endpoint: {}".format(self.ENDPOINT))
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
            self.result = pd.DataFrame(res['data'], columns=res["header"])

    def books_search(self, **query):
        """ Takes 0 or many arguments. E.g. Title="two citites", Author="Dickens" """
        q = self.ENDPOINT + "/books_search?"
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
            self.result = pd.DataFrame(res['data'], columns=res["header"])

    def book(self, book_collection_id):
        """ Takes 1 argument."""
        q = self.ENDPOINT + f"/books_search?BookCollectionID={book_collection_id}"
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
                self.result = book_collection_id

    def books_read_by_year_with_summary(self, year=None):
        """ Takes 0 or 1 argument."""
        self.result = []
        q = self.ENDPOINT + "/summary_books_read_by_year"
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
                q = self.ENDPOINT + f"/books_read/{year}"
                try:
                    tr = requests.get(q)
                    tres = tr.json()
                except requests.RequestException as e:
                    logging.error(e)
                else:
                    self.result.append(pd.DataFrame(tres['data'], columns=tres["header"]))
                    _data.extend(tres["data"])
                    _template = ["" for i in range(len(tres["data"][0]))]
                    _template[0] = f" **** {year} ****"
                    _template[1] = f"Books = {books}"
                    _template[2] = f"Pages = {pages}"
                    _data.append(_template)
            self._show_table(_data, tres["header"], self.MINIMAL_BOOK_INDEXES)

    def books_read_by_year(self, year=None):
        """ Takes 0 or 1 argument."""
        q = self.ENDPOINT + "/books_read"
        if year is not None:
            q += f"/{year}"
        try:
            tr = requests.get(q)
            tres = tr.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            self._show_table(tres["data"], tres["header"], self.MINIMAL_BOOK_INDEXES)
            self.result = pd.DataFrame(tres['data'], columns=tres["header"])

    def summary_books_read_by_year(self, year=None):
        """ Takes 0 or 1 argument."""
        q = self.ENDPOINT + "/summary_books_read_by_year"
        if year is not None:
            q += f"/{year}"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            self._show_table(res["data"], res["header"], [0, 1, 2])
            self.result = pd.DataFrame(res['data'], columns=res["header"])

    def add_books(self, n=1):
        """ Takes 0 argument."""
        records = [self._populate_new_book_record() for i in range(n)]
        q = self.ENDPOINT + "/add_books"
        try:
            tr = requests.post(q, json=records)
            tres = tr.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            ids = []
            for rec in tres["add_books"]:
                ids.append(rec["BookCollectionID"])
            self.result = ids

    def update_read_books(self, id_list):
        """ Takes 1 argument."""
        records = [self._populate_update_read_dates(id) for id in id_list]
        q = self.ENDPOINT + "/update_read_dates"
        try:
            tr = requests.post(q, json=records)
            tres = tr.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            ids = []
            for rec in tres["update_read_dates"]:
                ids.append(rec["BookCollectionID"])
            self.result = ids


if __name__ == "__main__":
    rpl = BC_Tool()
    rpl.tag_counts()
    rpl.books_search(Title="science")
