import json

import requests as req


class Endpoint:
    CONFIG_PATH = "/book_service/config/configuration.json"

    def __init__(self):
        try:
            infile = open(f".{self.CONFIG_PATH}", "r")
        except OSError:
            try:
                infile = open(f"..{self.CONFIG_PATH}", "r")
            except OSError:
                print("Configuration file not found!")
        with infile:
            self.config = json.load(infile)["isbn_com"]

    def get_book_by_isbn(self, isbn=None):
        headers = {'Authorization': self.config["key"]}
        url = self.config["url_isbn"].format(isbn)
        resp = req.get(url, headers=headers)
        return resp.json()

    def get_books_by_isbn_list(self, isbn_list=[]):
        result = {}
        for isbn in isbn_list:
            result[isbn] = self.get_book_by_isbn(isbn)
        return result
