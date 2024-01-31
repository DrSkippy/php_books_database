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

    def new_book_estimate(self, book_id, total_readable_pages):
        q = self.end_point + f"/add_book_estimate/{book_id}/{total_readable_pages}"
        try:
            tr = requests.put(q, headers=self.header)
            tres = tr.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            if "error" in tres:
                print(f'Error: {tres["error"]}')
            else:
                print(f'{tres["BookCollectionID"]} started on {tres["StartDate"]}.')
        self.list_book_estimates(book_id)

    def list_book_estimates(self, book_id):
        q = self.end_point + f"/record_set/{book_id}/-1"
        try:
            tr = requests.get(q, headers=self.header)
            tres = tr.json()["record_set"]
        except requests.RequestException as e:
            logging.error(e)
        else:
            if "error" in tres:
                print(f'Error: {tres["error"]}')
            elif len(tres) > 0:
                print("*" * WIDTH)
                print(f'BookCollectionID: {book_id}')
                for [k,v] in tres["RecordID"]:
                    print(f'  Start date: {k}   Record ID: {v}')
                print("*" * WIDTH)
        self.result = tres["RecordID"][-1][1]

    def add_date_pages(self, record_id, page, date=None):
        if date is None:
            date = datetime.datetime.now().strftime(FMT)
        # find record id
        q = self.end_point + f"/add_date_page"
        payload = {"RecordID": record_id, "RecordDate": date, "Page": page}
        try:
            tr = requests.post(q, json=payload, headers=self.header)
            res = tr.json()
        except requests.RequestException as e:
            logging.error(e)
        else:
            if "error" in res:
                logging.error(f'Error: {res["error"]}')
            else:
                res = res["add_date_page"]
                print(f'{res["RecordID"]} read to page {res["Page"]} on {date}.')
        self.result = record_id

    def estimate(self, record_id):
        try:
            q0 = self.end_point + f"/book_id_from_record_id/{record_id}"
            book_id_record = requests.get(q0, headers=self.header)
            book_id = book_id_record.json()["BookCollectionID"]
            #
            q1 = self.end_point + f"/books_search?BookCollectionID={book_id}"
            br = requests.get(q1, headers=self.header)
            bres = br.json()["data"][0]
            #
            q2 = self.end_point + f"/estimate/{record_id}"
            tr = requests.get(q2, headers=self.header)
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
        self.result = record_id
