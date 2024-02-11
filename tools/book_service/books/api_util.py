import datetime
import functools
import json
import logging
from decimal import Decimal

import numpy as np
import pymysql
from flask import request, abort

logger = logging.getLogger('app.py.sub')

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
            logger.error(e)
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
        config_filename = "./config/configuration.json"
        with open(config_filename, "r") as config_file:
            c = json.load(config_file)
            key = c["api_key"].replace('\n', '')
        # Select one of these:
        # if request.args.get('key') and request.args.get('key') == key:
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') == key:
            return view_function(*args, **kwargs)
        else:
            abort(401)

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


##########################################################################
# REPORTS
##########################################################################

def _summary_books_read_by_year(target_year=None):
    """
    Summarizes the number of pages read and books read each year.
    Can be filtered for a specific year.

    Parameters:
    target_year (int, optional): The year for which the summary is required. Defaults to None.

    Returns:
    tuple: A tuple containing the serialized result, raw data, and header.
    """
    # Initialize database connection
    db = pymysql.connect(**conf)
    cursor = db.cursor()

    # Building the SQL query string
    query = (
        "SELECT YEAR(b.ReadDate) as Year, SUM(a.Pages) as Pages, COUNT(a.Pages) as Books "
        "FROM `book collection` as a JOIN `books read` as b "
        "ON a.BookCollectionID = b.BookCollectionID "
        "WHERE b.ReadDate is not NULL "
    )
    if target_year is not None:
        query += f" AND YEAR(b.ReadDate) = {target_year} "
    query += "GROUP BY Year ORDER BY Year ASC"

    # Prepare response data
    headers = ["year", "pages read", "books read"]
    app.logger.debug(query)

    # Execute query and handle exceptions
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        serialized_data = serialize_rows(results, headers)
    except pymysql.Error as e:
        app.logger.error(e)
        serialized_data = json.dumps({"error": str(e)})
        results = None
    finally:
        # Close the database connection
        db.close()

    return serialized_data, results, headers


def _books_read(target_year=None):
    db = pymysql.connect(**conf)
    search_str = ("SELECT a.BookCollectionID, a.Title, a.Author, a.CopyrightDate, "
                  "a.ISBNNumber, a.PublisherName, a.CoverType, a.Pages, "
                  "a.Category, a.Note, a.Recycled, a.Location, a.ISBNNumber13, "
                  "b.ReadDate "
                  "FROM `book collection` as a JOIN `books read` as b "
                  "ON a.BookCollectionID = b.BookCollectionID "
                  "WHERE b.ReadDate is not NULL ")
    if target_year is not None:
        search_str += f" AND YEAR(b.ReadDate) = {target_year} "
    search_str += "ORDER BY b.ReadDate"
    header = table_header + ["ReadDate"]
    app.logger.debug(search_str)
    s = None
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app.logger.error(e)
        rdata = json.dumps({"error": str(e)})
    else:
        s = c.fetchall()
        rdata = serialize_rows(s, header)
    return rdata, s, header


def _tags_search(match_str):
    match_str = match_str.lower().strip()
    db = pymysql.connect(**conf)
    search_str = ("SELECT a.BookID, b.TagID, b.Label as Tag"
                  " FROM `books tags` a JOIN `tag labels` b ON a.TagID=b.TagID"
                  f" WHERE b.Label LIKE \"%{match_str}%\" "
                  " ORDER BY b.Label ASC")
    header = ["BookCollectionID", "TagID", "Tag"]
    app.logger.debug(search_str)
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app.logger.error(e)
        rdata = json.dumps({"error": str(e)})
    else:
        s = c.fetchall()
        rdata = serialize_rows(s, header)
    return rdata, s, header


##########################################################################
# READING ESTIMATES
#########################################################################

def _estimate_range(x, y, p):
    res = [0, 10000]
    for i in range(len(x) - 1):
        # Find max and min slopes
        m = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
        est = int(m * (p - np.max(x)) + np.max(y))
        if est > res[0]:
            res[0] = est
        if est < res[1]:
            res[1] = est
    return res  # (max, min)


def _line_fit_and_estimate(data, total_pages):
    d = np.array(data)
    x = np.array(d[:, 1], dtype=np.float64)
    y = np.array(d[:, 2], dtype=np.float64)
    m, b = np.polyfit(x, y, 1)
    est = m * float(total_pages) + b
    est_range = _estimate_range(x, y, total_pages)
    return int(est), est_range


def daily_page_record_from_db(RecordID):
    """
    Fetches daily page records for a specified RecordID from the database.

    Adds a day number column to each record, indicating the number of days since the first record.

    Parameters:
    RecordID (int): The ID for which daily page records are to be fetched.

    Returns:
    tuple: A tuple containing the modified list of records and the RecordID.
    """
    # Initialize an empty list for the data
    data = []

    # Connect to the database
    try:
        db = pymysql.connect(**conf)
        with db.cursor() as cur:
            # Execute the query to fetch daily page records
            cur.execute("SELECT a.RecordDate, a.page FROM `daily page records` a "
                        "WHERE a.RecordID = %s ORDER BY a.RecordDate ASC", (RecordID,))
            rows = cur.fetchall()

            # Check if any rows were returned
            if rows:
                start_date = rows[0][0]
                for row in rows:
                    # Calculate the day number and append it to the row
                    day_number = (row[0] - start_date).days
                    data.append(list(row) + [day_number])
    except pymysql.MySQLError as e:
        logger.error(f"Database error: {e}")
    finally:
        # Ensure the database connection is closed
        db.close()

    return data, RecordID


# def daily_page_record_from_db(RecordID):
#     data = []
#     db = pymysql.connect(**conf)
#     with db:
#         with db.cursor() as cur:
#             cur.execute("SELECT a.RecordDate, a.page FROM `daily page records` a "
#                         "WHERE a.RecordID = %s ORDER BY a.RecordDate ASC;", RecordID)
#             rows = cur.fetchall()
#             if len(rows) > 0:
#                 start_date = rows[0][0]
#                 for row in rows:
#                     data.append(list(row) + [(row[0] - start_date).days]) # add day number column
#     return data, RecordID


def reading_book_data_from_db(RecordID):
    """
    Fetches book data for a specified RecordID from the database.

    Excludes the BookCollectionID and RecordID from the returned data.

    Parameters:
    RecordID (int): The ID for which book data is to be fetched.

    Returns:
    tuple: A tuple containing the list of book data records and the RecordID.
    """
    # Initialize an empty list for the data
    rows = []

    # Establish a database connection
    try:
        db = pymysql.connect(**conf)
        with db.cursor() as cur:
            # Execute the query to fetch book data
            cur.execute("SELECT StartDate, LastReadablePage FROM `complete date estimates` WHERE RecordID = %s", (RecordID,))
            rows = cur.fetchall()

            # Process each row to exclude the first and last columns
#             for row in rows:
#                 data.append(list(row[1:-1]))  # Exclude the first and last column
    except pymysql.MySQLError as e:
        # Handle database errors
        logger.error(f"Database error: {e}")
    finally:
        # Ensure the database connection is closed
        db.close()

    return rows, RecordID


# def reading_book_data_from_db(RecordID):
#     data = []
#     db = pymysql.connect(**conf)
#     with db:
#         with db.cursor() as cur:
#             cur.execute("SELECT * FROM `complete date estimates` WHERE RecordID = %s", RecordID)
#             rows = cur.fetchall()
#             for row in rows:
#                 data.append(list(row[1:-1])) # don't include BookCollectionID or RecordID
#     return data, RecordID


def update_reading_book_data(record_id, date_range):
    db = pymysql.connect(**conf)
    with db:
        with db.cursor() as c:
            try:
                c.execute(
                    "UPDATE `complete date estimates` SET EstimateDate = %s, EstimatedFinishDate = %s WHERE RecordID = %s",
                    (datetime.datetime.now(), date_range[0], record_id))
            except pymysql.Error as e:
                logger.error(e)
        db.commit()


def estimate_dates(data, start_date, total_readable_pages):
    estimated_completion_days, estimated_range = _line_fit_and_estimate(data, float(total_readable_pages))
    estimated_completion_date = start_date + datetime.timedelta(days=estimated_completion_days)
    est_date_max = start_date + datetime.timedelta(days=estimated_range[0])
    est_date_min = start_date + datetime.timedelta(days=estimated_range[1])
    return estimated_completion_date, est_date_min, est_date_max

# def calculate_estimates(record_id):
#     reading_data, _ = daily_page_record_from_db(record_id)
#     if len(reading_data) < 2:
#         return ["inadequate reading data", None, None]
#     book_data, _ = reading_book_data_from_db(record_id)
#     estimate_date_range = estimate_dates(reading_data, book_data[0][0], book_data[0][1])
#     update_reading_book_data(record_id, estimate_date_range)
#     return [x.strftime(FMT) for x in estimate_date_range]
#
#
# from datetime import datetime

# Assuming FMT is defined elsewhere, e.g., FMT = '%Y-%m-%d'

def calculate_estimates(record_id):
    """
    Calculates date estimates for a book based on reading and book data.

    Parameters:
    record_id (int): The ID of the book record for which estimates are calculated.

    Returns:
    list: A list containing formatted estimated date range or an error message.
    """
    # Fetch daily page record from the database
    reading_data, _ = daily_page_record_from_db(record_id)
    if len(reading_data) < 2:
        return ["inadequate reading data", None, None]

    # Fetch book data from the database
    book_data, _ = reading_book_data_from_db(record_id)
    if not book_data:
        return ["inadequate book data", None, None]
    [start_date, total_readable_pages] = book_data[0]

    # Calculate the estimate date range
    estimate_date_range = estimate_dates(reading_data, start_date, total_readable_pages)

    # Update the database with the estimated date range
    update_reading_book_data(record_id, estimate_date_range)

    # Format the estimated date range for output
    formatted_estimates = [date.strftime(FMT) for date in estimate_date_range]

    return formatted_estimates
