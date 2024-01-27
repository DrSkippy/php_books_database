import datetime

FMT = "%Y-%m-%d"

def new(book_id,  total_readable_pages):
    q = self.ENDPOINT + f"/add_book_estimate/{book_id}/{total_readable_pages}"
    try:
        tr = requests.get(q)
        tres = tr.json()
    except requests.RequestException as e:
        logging.error(e)
    if "error" in tres:
        print(f"Error: {tres["error"]}")
    else:
        print(f'{tres["BookCollectionID"]} started on {tres["StartDate"].strftime(FMT)}.')
    return = book_id

def add_date_pages(book_id, page, date=None):
    if date is None:
        date = datetime.datetime.now().strftime(FMT)
    q = self.ENDPOINT + f"/add_date_page"
    payload = {"BookCollectionID": book_id, "RecordDate": date, "Page": page}
    try:
        tr = requests.post(q, json=payload)
        res = tr.json()["add_date_page"]
    except requests.RequestException as e:
        logging.error(e)
    if "error" in res:
        print(f"Error: {res["error"]}")
    else:
        print(f'{res["BookCollectionID"]} read to page {res["page"]} on {date.strftime(FMT)}.')
    result = book_id

def make(book_id):
    q = self.ENDPOINT + f"/estimate/{book_id}"
    try:
        tr = requests.get(q)
        tres = tr.json()
    except requests.RequestException as e:
        logging.error(e)
    if "error" in tres:
        print(f"Error: {tres["error"]}")
    else:
        print(f'{tres["BookCollectionID"]} estimated finish on {tres["estimate"][0]}.')
        print(f'  Earliest: {tres["estimate"][1]} Latest: {tres["estimate"][2]}.')
    result = book_id

