import datetime
import functools
import json
from decimal import Decimal

from flask import request, abort

table_header = ["BookCollectionID", "Title", "Author", "CopyrightDate", "ISBNNumber", "PublisherName",
                "CoverType", "Pages", "Category", "Note", "Recycled",
                "Location", "ISBNNumber13"]

locations_sort_order = [3, 4, 2, 1, 7, 6, 5]


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
