import logging

import requests


class REPL_Tool:
    ENDPOINT = "http://192.168.127.8/books"

    def __init__(self):
        pass

    def show_tags(self, bookid=None):
        try:
            r = requests.get(self.ENDPOINT + "/tag_counts")
            res = r.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            for j in res["data"]:
                print("{:25s}: {:4d}".format(*j))

    def books(self, **query):
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
            for j in res["data"]:
                print("{:12d} | {:75s}\n             | {:25s}".format(*j[:3]))


if __name__ == "__main__":
    rpl = REPL_Tool()
    rpl.show_tags()
    rpl.books(Title="science")
