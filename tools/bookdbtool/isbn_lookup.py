from pprint import pprint
import requests as req


class ISBNLookup:

    def __init__(self, config):
        self.config = config
        self.result = None

    def lookup(self, isbn=None):
        _result = None
        if isinstance(isbn, list):
            _result = {}
            for _isbn in isbn:
                self._lookup(_isbn)
                _result[_isbn] = self.result
                a = input("Return to continue; q to quit...") if _isbn != isbn[-1] else ""
                if a.startswith("q"):
                    break
            self.result = _result
        elif isbn:
            self._lookup(isbn)

    def _lookup(self, isbn):
        headers = {'Authorization': self.config["key"]}
        url = self.config["url_isbn"].format(isbn)
        resp = req.get(url, headers=headers)
        pprint(resp.json(), indent=3)
        self.result = resp.json()
