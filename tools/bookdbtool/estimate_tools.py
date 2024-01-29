import datetime
import logging
import requests

FMT = "%Y-%m-%d"
WIDTH = 72

class EST_Tool:
    def __init__(self, endpoint, api_key):
        # File path contortions so notebook uses the same config as REPL command line
        self.end_point = endpoint
        self.header = {"x-api-key": f"{api_key}"}
        self.result = None

    def new(self, book_id, total_readable_pages):
        q = self.end_point + f"/add_book_estimate/{book_id}/{total_readable_pages}"
        try:
            tr = requests.get(q, headers=self.header)
            tres = tr.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            if "error" in tres:
                print(f'Error: {tres["error"]}')
            else:
                print(f'{tres["BookCollectionID"]} started on {tres["StartDate"].strftime(FMT)}.')
        self.result = book_id

    def add_date_pages(self, book_id, page, date=None):
        if date is None:
            date = datetime.datetime.now().strftime(FMT)
        q = self.end_point + f"/add_date_page"
        payload = {"BookCollectionID": book_id, "RecordDate": date, "Page": page}
        try:
            tr = requests.post(q, json=payload, headers=self.header)
            res = tr.json()["add_date_page"]
        except requests.RequestException as e:
            logging.error(e)
        else:
            if "error" in res:
                logging.error(f'Error: {res["error"]}')
            else:
                print(f'{res["BookCollectionID"]} read to page {res["page"]} on {date.strftime(FMT)}.')
        self.result = book_id

    def make(self, book_id):
        q = self.end_point + f"/estimate/{book_id}"
        q1 = self.end_point + f"/books_search?BookCollectionID={book_id}"
        try:
            br = requests.get(q1, headers=self.header)
            bres = br.json()["data"][0]
            tr = requests.get(q, headers=self.header)
            tres = tr.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            if "error" in tres:
                logging.error(f'Error: {tres["error"]}')
            else:
                print("*" * WIDTH)
                print(f'"{bres[1]}" by {bres[2]} has {bres[7]} pages.\n')
                print(f'"{bres[1]}" estimated finish on {tres["estimate"][0]}.')
                print(f'  Earliest: {tres["estimate"][1]} Latest: {tres["estimate"][2]}.')
                print("*" * WIDTH)
        self.result = book_id
