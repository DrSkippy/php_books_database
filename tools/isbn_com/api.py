import requests as req
import json

class endpoint:

    CONFIG_FILENAME = "./configuration.json"

    def __init__(self):
        with open(self.CONFIG_FILENAME, "r") as infile:
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

