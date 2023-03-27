__version__ = '0.5.3'

import datetime
import logging
import os
import pprint

pp = pprint.PrettyPrinter(indent=3)

import pandas as pd
import requests
from columnar import columnar



class BC_Tool:
    ENDPOINT = "http://192.168.127.8/books"
    # ENDPOINT = "http://192.168.127.6:83"
    # ENDPOINT = "http://172.17.0.2:8083"
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
    COLLECTION_DB_DICT = {
        "Title": "",
        "Author": "",
        "CopyrightDate": "2000-01-01",
        "ISBNNumber": "",
        "ISBNNumber13": "",
        "PublisherName": "",
        "CoverType": "Digital, Hard, Soft",
        "Pages": 0,
        "Location": "Main Collection, DOWNLOAD, Oversized, Pets, Woodwork, Reference, Birding",
        "Note": "",
        "Recycled": "0=No or 1=Yes"
    }
    MINIMAL_BOOK_INDEXES = [0, 1, 2, 7, 9, 10, 11, 13]
    page_size = 35
    terminal_width = 180
    LINES_TO_ROWS = 1.3
    DIVIDER_WIDTH = 50

    def __init__(self):
        self.result = None

    def _row_column_selector(self, row, indexes):
        return [row[i] for i in indexes]

    def _column_selector(self, data, indexes):
        return [self._row_column_selector(i, indexes) for i in data]

    def _show_table(self, data, header, indexes, pagination=True):
        [self.terminal_width, page_size] = os.get_terminal_size()
        if pagination:
            self.page_size = int(page_size / self.LINES_TO_ROWS)
        else:
            self.page_size = 10000
        try:
            i = 0
            while i < len(data):
                d = len(data) - i if len(data) - i < self.page_size else self.page_size
                print(columnar(self._column_selector(data[i:i + d], indexes),
                               self._row_column_selector(header, indexes),
                               terminal_width=self.terminal_width,
                               no_borders=True))
                i += d
                a = input("Return to continue; q to quit...") if i < len(data) else ""
                if a.startswith("q"):
                    break
        except TypeError as e:
            print("No data")

    def _populate_new_book_record(self):
        proto = self.COLLECTION_DB_DICT.copy()
        return self._inputer(proto)

    def _populate_add_read_date(self, book_collection_id, today=True):
        proto = {
            "BookCollectionID": book_collection_id,
            "ReadDate": datetime.date.today().strftime("%Y-%m-%d"),
            "ReadNote": ""
        }
        return self._inputer(proto, exclude_keys=["BookCollectionID"])

    def _inputer(self, proto, exclude_keys=[]):
        verified = False
        while not verified:
            for key in proto:
                if key in exclude_keys:
                    print(f"{key}: {proto[key]}")
                else:
                    a = input(f"{key} ({proto[key]}     'a' to accept): ")
                    a = a.strip()
                    if a != "a":
                        proto[key] = a
            print("*" * self.DIVIDER_WIDTH)
            pp.pprint(proto)
            a = input("'x' to try again, 'a' to accept: ")
            a = a.strip()
            if a == "a":
                verified = True
        return proto

#     def _endpoint_to_collection_db(self, isbn_dict):
#         proto = self.COLLECTION_DB_DICT.copy()
#         proto["Title"] = isbn_dict["book"]["title"]
#         proto["Author"] = isbn_dict["book"]["authors"][0]
#         proto["ISBNNumber"] = isbn_dict["book"]["isbn"]
#         proto["ISBNNumber13"] = isbn_dict["book"]["isbn13"]
#         try:
#             proto["PublisherName"] = isbn_dict["book"]["publisher"]
#         except KeyError:
#             proto["PublisherName"] = "unknown"
#         proto["Pages"] = isbn_dict["book"]["pages"]
#         try:
#             _pub = str(isbn_dict["book"]["date_published"])[:10]  # yyyy-mm-dd
#             if len(_pub) == 4:
#                 _pub += "-01-01"
#             proto["CopyrightDate"] = _pub
#         except KeyError:
#             proto["CopyrightDate"] = "0000-01-01"
#         return proto

    def _add_books(self, records):
        result_message = "Added."
        q = self.ENDPOINT + "/add_books"
        try:
            tr = requests.post(q, json=records)
            tres = tr.json()
        except requests.RequestException as e:
            logging.error(e)
            result_message = {"errors": [str(e)]}
        else:
            book_collection_id_list = []
            for rec in tres["add_books"]:
                book_collection_id_list.append(rec["BookCollectionID"])
            self.result = book_collection_id_list
        return result_message

    def version(self):
        """ Retrieve the back end version. """
        q = self.ENDPOINT + "/configuration"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            print("*" * self.DIVIDER_WIDTH)
            print("        Book Records and Reading Database")
            print("*" * self.DIVIDER_WIDTH)
            print("Endpoint:         {}".format(self.ENDPOINT))
            print("Endpoint Version: {}".format(res["version"]))
            print("Client Version:   {}".format(__version__))
            print("*" * self.DIVIDER_WIDTH)

    ver = version

    def columns(self):
        """
        Show the book collection database columns.
        """
        print("\n".join(list(self.COLUMN_INDEX.keys())))

    col = columns

    def tag_counts(self, tag=None, pagination=True):
        """
        Arguments
            tag: String for which you want a tag count. Required.
            pagination: True or False. Default is True to paginate the results according to the screen size.
        """
        q = self.ENDPOINT + "/tag_counts"
        if tag is not None:
            q += f"/{tag}"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            self._show_table(res["data"], res["header"], [0, 1], pagination)
            self.result = pd.DataFrame(res['data'], columns=res["header"])

    tc = tag_counts

    def books_search(self, **query):
        """
        Arguments
            query is optional, use named variables for columns you wish to match.
                E.g. bc.book_search(Title="two cities", Author="Dickens")

        Use bc.columns() to see a list of columns.
        bc.result is a Pandas DataFrame.
        """
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

    bs = books_search

    def tags_search(self, match_str, pagination=True, output=True):
        """
        Arguments
            match_str is string that partially aor fully matches a tag in the database.
            pagination: True or False. Default is True to paginate the results according to the screen size.
        Returns
            List of tags matching match_str.
            bc.result is a list of book collection ids for books with matching tag.
        """
        q = self.ENDPOINT + f"/tags_search/{match_str}"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            if output:
                self._show_table(res["data"], res["header"], [0, 1, 2], pagination)
            self.result = set([x[0] for x in res["data"]])

    ts = tags_search

    def book(self, book_collection_id, pagination=True):
        """
        Argument
            book_collection_id for the book you wish to retrieve. Required.
            pagination: True or False. Default is True to paginate the results according to the screen size.Takes 1 argument.
        Returns
            Book records with tag list and read status.
            bc.result is a book collection id.
        """
        assert isinstance(book_collection_id, int), "Requires in integer Book ID"
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
                self._show_table(_data, res["header"], self.MINIMAL_BOOK_INDEXES, pagination)
                self.result = book_collection_id

    def books_read_by_year_with_summary(self, year=None, pagination=True):
        """
        Arguments
            year is the 4 digit year of for which you want a summary. Options, blank returns all books read.
            pagination: True or False. Default is True to paginate the results according to the screen size.Takes 1 argument.
        Returns
            table of books for each year with a yearly summary.
            bc.result is a list of Pandas DataFrames.
        """
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
                    _template = [" " for i in range(len(tres["data"][0]))]
                    _data.append(_template)
                    self.result.append(pd.DataFrame(tres['data'], columns=tres["header"]))
                    _data.extend(tres["data"])
                    _template = ["" for i in range(len(tres["data"][0]))]
                    _template[0] = f" **** {year} ****"
                    _template[1] = f"Books = {books}"
                    _template[2] = f"Pages = {pages}"
                    _data.append(_template)
            self._show_table(_data, tres["header"], self.MINIMAL_BOOK_INDEXES, pagination)

    brys = books_read_by_year_with_summary

    def books_read_by_year(self, year=None, pagination=True):
        """
        Arguments
            year is the 4 digit year of for which you want a list. Options, blank returns all books read.
            pagination: True or False. Default is True to paginate the results according to the screen size.Takes 1 argument.
        Returns
            table of books for years.
            bc.result is a Pandas DataFrame.
        """
        q = self.ENDPOINT + "/books_read"
        if year is not None:
            q += f"/{year}"
        try:
            tr = requests.get(q)
            tres = tr.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            self._show_table(tres["data"], tres["header"], self.MINIMAL_BOOK_INDEXES, pagination)
            self.result = pd.DataFrame(tres['data'], columns=tres["header"])

    bry = books_read_by_year

    def summary_books_read_by_year(self, year=None, show=True, pagination=True):
        """
        Arguments
            year is the 4 digit year of for which you want a list. Options, blank returns all books read.
            show=False will put results in bc.result, but will not print the list
            pagination: True or False. Default is True to paginate the results according to the screen size.Takes 1 argument.
        Returns
            table of books for years.
            bc.result is a Pandas DataFrame.
        """
        q = self.ENDPOINT + "/summary_books_read_by_year"
        if year is not None:
            q += f"/{year}"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            self._show_table(res["data"], res["header"], [0, 1, 2], pagination) if show else None
            self.result = pd.DataFrame(res['data'], columns=res["header"])

    sbry = summary_books_read_by_year

    def year_rank(self, df=None, pages=True):
        """
        Arguments
            df is a Pandas Dataframe with summary information (see summary_books_read_by_year). Optional.
            pages=True sort by pages read per year; False gives sort by books read per year.
        Returns
            table of books for years.
            bc.result is a Pandas DataFrame.
        """
        if df is None:
            self.summary_books_read_by_year(show=False)
            df = self.result
        if pages:
            df = df.sort_values("pages read", ascending=False)
        else:
            df = df.sort_values("books read", ascending=False)
        df.reset_index(inplace=True, drop=True)
        print("\n", df)
        self.result = df

    def add_books(self, n=1):
        """
        Creates records interactively and adds to the collection.
        Arguments
            n is the number of books to add to the collection.
        Returns
            None or error
            bc.result is list of book_collection_ids added.
        """
        res = None
        records = [self._populate_new_book_record() for i in range(n)]
        res = self._add_books(records)
        return res

    ab = add_books

    def add_books_by_isbn(self, book_isbn_list):
        """
        Creates records from isbn lookup and adds to the collection.
        Arguments
            List of isbns (strings) of the books you wish to add to the collection. Required.
        Returns
            None or error
            bc.result is list of ids added.
        """
        q = self.ENDPOINT + "/books_by_isbn"
        payload = {"isbn_list": book_isbn_list}
        try:
            tr = requests.post(q, json=payload)
            book_record_list = tr.json()["book_records"]
        except requests.RequestException as e:
            logging.error(e)
        res = []
        for book_json, book_isbn in zip(book_record_list, book_isbn_list):
            if book_json is not None:
                proto = self._inputer(book_json)
                records = [proto]
                self.result = proto
                res.append(self._add_books(records))
            else:
                logging.error(f"No records found for isbn {book_isbn}.")
        return res

    abi = add_books_by_isbn

    def add_read_books(self, book_collection_id_list):
        """ Takes 1 argument.
        Update records for BookCollectionIds in list provided. """
        records = [self._populate_add_read_date(id) for id in book_collection_id_list]
        q = self.ENDPOINT + "/add_read_dates"
        try:
            tr = requests.post(q, json=records)
            tres = tr.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            new_book_collection_id_list = []
            for rec in tres["update_read_dates"]:
                new_book_collection_id_list.append(rec["BookCollectionID"])
            self.result = new_book_collection_id_list

    arb = add_read_books

    def update_tag_value(self, tag_value, new_tag_value, pagination=True):
        """ Takes 2 arguments,
        current value of tag and new value of tag """
        q = self.ENDPOINT + f"/update_tag_value/{tag_value}/{new_tag_value}"
        try:
            r = requests.get(q)
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            self._show_table(res["data"], res["header"], [0, 1, 2], pagination)
            self.result = pd.DataFrame(res['data'], columns=res["header"])

    def add_tags(self, book_collection_id, tags=[]):
        """ Takes 2 arguments.
        Arguments
            book_collection_id is the BookCollectionID of the target book record
            tags is a list of tags to add (strings)
        Returns
            bc.result is the book_collection_id
        """
        assert isinstance(book_collection_id, int), "Requires in integer Book ID"
        q = self.ENDPOINT + f"/add_tag/{book_collection_id}/" + "{}"
        result = {"data": [], "error": []}
        for t in tags:
            try:
                r = requests.put(q.format(t))
                res = r.json()
                if "error" in res:
                    result["error"].append(res["error"])
                else:
                    result["data"].append(res)
            except requests.RequestException as e:
                logging.error(e)
                result["error"].append(e)
        else:
            print("Added {} tags to book with id={}".format(len(result["data"]), book_collection_id))
            if len(result["error"]) > 0:
                print(" with errors={}".format(", ".join(result["error"])))
            self.result = book_collection_id

    at = add_tags


if __name__ == "__main__":
    rpl = BC_Tool()
    rpl.tag_counts()
    rpl.books_search(Title="science")
