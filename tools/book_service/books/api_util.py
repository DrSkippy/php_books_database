import datetime
import functools
import json
from decimal import Decimal

import numpy as np
import pymysql


table_header = ["BookCollectionID", "Title", "Author", "CopyrightDate", "ISBNNumber", "PublisherName",
                "CoverType", "Pages", "Category", "Note", "Recycled",
                "Location", "ISBNNumber13"]

locations_sort_order = [3, 4, 2, 1, 7, 6, 5]

FMT = "%Y-%m-%d"


def get_configuration():
    config_filename = "./config/configuration.json"
    with open(config_filename, "r") as config_file:
        c = json.load(config_file)
        try:
            res = {
                "user": c["username"].strip(),
                "passwd": c["password"].strip(),
                "db": c["database"].strip(),
                "host": c["host"].strip(),
                "port": int(c["port"])
            }
            res1 = {
                "url_isbn": c["isbn_com"]["url_isbn"].strip(),
                "key": c["isbn_com"]["key"].strip()
            }
        except KeyError as e:
            print(e)
            sys.exit()
        return res, res1

# server configuration
conf, isbn_conf = get_configuration()

def sort_by_indexes(lst, indexes, reverse=False):
    return [val for (_, val) in sorted(zip(indexes, lst), key=lambda x: \
        x[0], reverse=reverse)]


def require_appkey(view_function):
    """
    Decorator to require API key for access
    :param view_function: any method that requires API key
    :return: endpoint method
    """

    @functools.wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        with open('./config/api.key', 'r') as apikey:
            key = apikey.read().replace('\n', '')
        # NO CONDITIONAL CHECK FOR KEY
        return view_function(*args, **kwargs)
        """
        # Select one of these:
        # if request.args.get('key') and request.args.get('key') == key:
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') == key:
            return view_function(*args, **kwargs)
        else:
            abort(401)
        """

    return decorated_function


def serialize_rows(cursor, header=None):
    """
    Provide a header here or output header will be None
    :param cursor: iterable results from pymysql query
    :param header: list of strings describing data to keep
    :return: json payload
    """
    result = {"header": header, "data": []}
    result_rows = []
    for row in cursor:
        _row = []
        if len(header) != len(row):
            print("mismatched header to data provided")
        for d in row:
            if isinstance(d, Decimal):
                _row.append(float(d))
            elif isinstance(d, datetime.datetime) or isinstance(d, datetime.date):
                _row.append(d.strftime("%Y-%m-%d"))
            else:
                _row.append(d)
        result_rows.append(_row)
    result["data"] = result_rows
    rdata = json.dumps(result)
    return rdata


def resp_header(rdata):
    response_header = [
        ('Access-Control-Allow-Origin', '*'),
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return response_header


def _estimate_range(x, y, p):
    res = [0, 10000]
    for i in range(len(x) - 1):
        m = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
        est = int(m * (p - np.max(x)) + np.max(y))
        if est > res[0]:
            res[0] = est
        if est < res[1]:
            res[1] = est
    return res


def _line_fit_and_estimate(data, total_pages):
    d = np.array(data)
    x = np.array(d[:, 1], dtype=np.float64)
    y = np.array(d[:, 2], dtype=np.float64)
    m, b = np.polyfit(x, y, 1)
    est = m * float(total_pages) + b
    est_range = _estimate_range(x, y, total_pages)
    return int(est), est_range


def daily_page_record_from_db(BookID):
    data = []
    db = pymysql.connect(**conf)
    with db:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM `daily page records` WHERE BookCollectionID = %s", BookID)
            rows = cur.fetchall()
            if len(rows) > 0:
                start_date = rows[0][1]
                for row in rows:
                    data.append(list(row[1:]) + [(row[1] - start_date).days])
    return data, BookID


def reading_book_data_from_db(BookID):
    data = []
    db = pymysql.connect(**conf)
    with db:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM `complete date estimates` WHERE BookCollectionID = %s", BookID)
            rows = cur.fetchall()
            for row in rows:
                data.append(list(row[1:]))
    return data, BookID


def update_reading_book_data(book_id, range):
    db = pymysql.connect(**conf)
    with db:
        with db.cursor() as c:
            try:
                c.execute(
                    "UPDATE `complete date estimates` SET EstimateDate = %s, EstimatedFinishDate = %s WHERE BookCollectionID = %s",
                    (datetime.datetime.now(), range[0], book_id))
            except pymysql.Error as e:
                app.logger.error(e)
        db.commit()


def estimate_dates(data, start_date, total_readable_pages):
    est, range = _line_fit_and_estimate(data, float(total_readable_pages))
    est_date = start_date + datetime.timedelta(days=est)
    est_date_max = start_date + datetime.timedelta(days=range[0])
    est_date_min = start_date + datetime.timedelta(days=range[1])
    return est_date, est_date_min, est_date_max
