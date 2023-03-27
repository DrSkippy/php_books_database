import requests as req
import json


class Endpoint:
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

    def __init__(self, conf):
        self.config = conf

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

    def _endpoint_to_collection_db(self, isbn_dict):
        proto = self.COLLECTION_DB_DICT.copy()
        proto["Title"] = isbn_dict["book"]["title"]
        proto["Author"] = isbn_dict["book"]["authors"][0]
        proto["ISBNNumber"] = isbn_dict["book"]["isbn"]
        proto["ISBNNumber13"] = isbn_dict["book"]["isbn13"]
        try:
            proto["PublisherName"] = isbn_dict["book"]["publisher"]
        except KeyError:
            proto["PublisherName"] = "unknown"
        proto["Pages"] = isbn_dict["book"]["pages"]
        try:
            _pub = str(isbn_dict["book"]["date_published"])[:10]  # yyyy-mm-dd
            if len(_pub) == 4:
                _pub += "-01-01"
            proto["CopyrightDate"] = _pub
        except KeyError:
            proto["CopyrightDate"] = "0000-01-01"
        return proto
