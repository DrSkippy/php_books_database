import datetime
import functools
import json
import logging
from decimal import Decimal

import numpy as np
import pymysql
from flask import request, abort

app_logger = logging.getLogger('app.py.sub')

table_header = ["BookCollectionID", "Title", "Author", "CopyrightDate", "ISBNNumber", "PublisherName",
                "CoverType", "Pages", "Category", "Note", "Recycled",
                "Location", "ISBNNumber13"]

locations_sort_order = [3, 4, 2, 1, 7, 6, 5]

FMT = "%Y-%m-%d"

API_KEY = None


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
            global API_KEY
            API_KEY = c["api_key"].replace('\n', '')
        except KeyError as e:
            app_logger.error(e)
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
        # Select one of these:
        # if request.args.get('key') and request.args.get('key') == key:
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            app_logger.error("x-api-key missing or incorrect.")
            abort(401)

    return decorated_function


def serialize_rows(cursor, header=None):
    """
    Provide a header here or output header will be None
    :param cursor: iterable results from pymysql query
    :param header: list of strings describing data to keep
    :return: json payload
    """
    result = result_dict(cursor, header)
    rdata = json.dumps(result)
    return rdata


def result_dict(cursor, header):
    """
    Converts the results of a database query into a dictionary format with a header and data.

    This function processes the rows returned by a database cursor and organizes them into a
    dictionary with two keys: 'header' and 'data'. The 'header' key contains the provided list
    of column names, and the 'data' key contains the rows of data, with each value formatted
    appropriately based on its type.

    Parameters:
    cursor (iterable): The database cursor containing the query results.
    header (list): A list of strings representing the column names for the data.

    Returns:
    dict: A dictionary with the following structure:
        {
            "header": [header],
            "data": [
                [row1_values],
                [row2_values],
                ...
            ]
        }
        - Decimal values are converted to floats.
        - datetime.date and datetime.datetime values are formatted as "YYYY-MM-DD".
        - Other values are included as-is.

    Notes:
    - If the length of the header does not match the length of a row, a warning message
      is printed to the console.
    """
    result = {"header": header, "data": []}  # Initialize the result dictionary
    result_rows = []  # List to store processed rows

    for row in cursor:  # Iterate over each row in the cursor
        _row = []  # Temporary list to store processed values for the current row
        if len(header) != len(row):  # Check if the header length matches the row length
            app_logger.debug("mismatched header to data provided")
        for d in row:  # Process each value in the row
            if isinstance(d, Decimal):  # Convert Decimal values to float
                _row.append(float(d))
            elif isinstance(d, datetime.datetime) or isinstance(d, datetime.date):  # Format dates
                _row.append(d.strftime("%Y-%m-%d"))
            else:  # Include other values as-is
                _row.append(d)
        result_rows.append(_row)  # Add the processed row to the result rows list

    result["data"] = result_rows  # Add the processed rows to the result dictionary
    return result  # Return the result dictionary


def resp_header(rdata):
    response_header = [
        ('Content-type', 'application/json; charset=utf-8'),
        ('Content-Length', str(len(rdata)))
    ]
    return response_header


##########################################################################
# BOOKS WINDOW
##########################################################################


def get_book_ids(book_id, window):
    db = pymysql.connect(**conf)
    app_logger.debug(f"Getting book ID window for book ID {book_id} with window {window}")
    top_half_window = int((window + 1) / 2)
    bottom_half_window = window - top_half_window

    query_str = ("SELECT a.BookCollectionID "
                 "FROM `book collection` as a "
                 "WHERE a.BookCollectionID {ineq} {book_id} "
                 "ORDER BY a.BookCollectionID {order} "
                 "LIMIT {limit};")
    # get the bottom half first - window leading up to book_id
    q = query_str.format(ineq="<=", book_id=book_id, order="DESC", limit=bottom_half_window)
    app_logger.debug(q)
    c = db.cursor()
    book_id_list = []
    try:
        c.execute(q)
    except pymysql.Error as e:
        app_logger.error(e)
    else:
        s = c.fetchall()
        for row in s:
            book_id_list.append(row[0])
        book_id_list.reverse()
    if len(book_id_list) < bottom_half_window:
        # Make a ring of ideas - get some from the end of book records
        deficit = bottom_half_window - len(book_id_list)
        q = query_str.format(ineq=">", book_id=book_id, order="DESC", limit=deficit)
        app_logger.debug(q)
        try:
            c.execute(q)
        except pymysql.Error as e:
            app_logger.error(e)
        else:
            s = c.fetchall()
            for row in s:
                book_id_list.insert(0, row[0])
    # now get the top half - window after book_id
    q = query_str.format(ineq=">", book_id=book_id, order="ASC", limit=top_half_window)
    app_logger.debug(q)
    try:
        c.execute(q)
    except pymysql.Error as e:
        app_logger.error(e)
    else:
        s = c.fetchall()
        for row in s:
            book_id_list.append(row[0])
    if len(book_id_list) < window:
        # Make a ring of ideas - get some from the start of book records
        deficit = window - len(book_id_list)
        q = query_str.format(ineq="<=", book_id=book_id, order="ASC", limit=deficit)
        app_logger.debug(q)
        try:
            c.execute(q)
        except pymysql.Error as e:
            app_logger.error(e)
        else:
            s = c.fetchall()
            for row in s:
                book_id_list.append(row[0])
    return book_id_list


def complete_book_record(book_id):
    # process any query parameters
    db = pymysql.connect(**conf)
    q_book = ("SELECT a.BookCollectionID, a.Title, a.Author, a.CopyrightDate, "
              "a.ISBNNumber, a.PublisherName, a.CoverType, a.Pages, "
              "a.Category, a.Note, a.Recycled, a.Location, a.ISBNNumber13 "
              "FROM `book collection` as a "
              f"WHERE a.BookCollectionID = {book_id};")
    h_book = table_header
    q_read = ("SELECT b.ReadDate, b.ReadNote "
              "FROM `books read` as b "
              f"WHERE b.BookCollectionID = {book_id};")
    h_read = ["DateRead", "ReadNote"]
    q_tags = ("SELECT b.Label "
              "FROM `books tags` as a JOIN `tag labels` as b "
              "ON b.TagID = a.TagID "
              f"WHERE a.BookID = {book_id};")
    h_tags = ["Tag"]
    app_logger.debug(q_book)
    app_logger.debug(q_read)
    app_logger.debug(q_tags)

    result_data = {"book": None, "reads": None, "tags": None, "error": []}
    c = db.cursor()
    try:
        c.execute(q_book)
    except pymysql.Error as e:
        app_logger.error(e)
        result_data["error"].append(str(e))
    else:
        s = c.fetchall()
        result_data["book"] = result_dict(s, h_book)
    try:
        c.execute(q_read)
    except pymysql.Error as e:
        app_logger.error(e)
        result_data["error"].append(str(e))
    else:
        s = c.fetchall()
        result_data["reads"] = result_dict(s, h_read)
    try:
        c.execute(q_tags)
    except pymysql.Error as e:
        app_logger.error(e)
        result_data["error"].append(str(e))
    else:
        s = c.fetchall()
        result_data["tags"] = result_dict([[x[0] for x in s]], h_tags)

    if len(result_data["error"]) == 0:
        del result_data["error"]
    return result_data


##########################################################################
# UPDATE BOOKS
##########################################################################

def update_book_record_by_key(update_dict):
    """
    Updates a book record in the database using the provided dictionary of record
    values and the corresponding `BookCollectionID`. Key-value pairs in the record
    represent the columns to update and their new values. If an error occurs while
    executing the SQL operation, an error dictionary will be returned.

    :param update_dict: A dictionary containing the record information for the book to
        be updated. The keys represent the column names, and the values represent
        the new data to be inserted for those columns.
    :type update_dict: dict
    :return: A list containing the result of the update operation. If successful,
        the `record` dictionary is returned; otherwise, an error dictionary is
        returned.
    :rtype: list
    """
    db = pymysql.connect(**conf)
    search_str = "UPDATE `book collection` SET "
    continuation = False
    for key in update_dict:
        if key == "BookCollectionID":
            BookCollectionID = update_dict[key]
            continue
        if continuation:
            search_str += ", "
        else:
            continuation = True
            search_str += f" {key} = \"{update_dict[key]}\""
    search_str += f" WHERE BookCollectionID = {BookCollectionID} "
    app_logger.debug(search_str)
    results = []
    with db:
        with db.cursor() as c:
            try:
                c.execute(search_str.format(**update_dict))
                app_logger.debug(search_str.format(**update_dict))
                results.append(update_dict)
            except pymysql.Error as e:
                app_logger.error(e)
                results.append({"error": str(e)})
        db.commit()
    return results


##########################################################################
# REPORTS
##########################################################################

def summary_books_read_by_year_utility(target_year=None):
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
    app_logger.debug(query)

    # Execute query and handle exceptions
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        serialized_data = serialize_rows(results, headers)
    except pymysql.Error as e:
        app_logger.error(e)
        serialized_data = json.dumps({"error": str(e)})
        results = None
    finally:
        # Close the database connection
        db.close()

    return serialized_data, results, headers


def books_read_utility(target_year=None):
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
    search_str += "ORDER BY b.ReadDate, a.BookCollectionID ASC"
    header = table_header + ["ReadDate"]
    app_logger.debug(search_str)
    s = None
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app_logger.error(e)
        rdata = json.dumps({"error": str(e)})
    else:
        s = c.fetchall()
        rdata = serialize_rows(s, header)
    return rdata, s, header


def tags_search_utility(match_str):
    match_str = match_str.lower().strip()
    db = pymysql.connect(**conf)
    search_str = ("SELECT a.BookID, b.TagID, b.Label as Tag"
                  " FROM `books tags` a JOIN `tag labels` b ON a.TagID=b.TagID"
                  f" WHERE b.Label LIKE \"%{match_str}%\" "
                  " ORDER BY b.Label ASC")
    header = ["BookCollectionID", "TagID", "Tag"]
    app_logger.debug(search_str)
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app_logger.error(e)
        rdata = json.dumps({"error": str(e)})
    else:
        s = c.fetchall()
        rdata = serialize_rows(s, header)
    return rdata, s, header


##########################################################################
# READING ESTIMATES
#########################################################################


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
            q = ("SELECT a.RecordDate, a.page FROM `daily page records` a "
                 f"WHERE a.RecordID = {RecordID} ORDER BY a.RecordDate ASC")
            app_logger.debug(q)
            cur.execute(q)
            rows = cur.fetchall()

            # Check if any rows were returned
            if rows:
                first_record_date = rows[0][0]
                for row in rows:
                    # Calculate the day number and append it to the row
                    day_number = (row[0] - first_record_date).days
                    data.append(list(row) + [day_number])
    except pymysql.MySQLError as e:
        app_logger.error(f"Database error: {e}")
    finally:
        # Ensure the database connection is closed
        db.close()

    return data, RecordID


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
            q = f'SELECT StartDate, LastReadablePage FROM `complete date estimates` WHERE RecordID = {RecordID}'
            app_logger.debug(q)
            cur.execute(q)
            rows = cur.fetchall()
    except pymysql.MySQLError as e:
        # Handle database errors
        app_logger.error(f"Database error: {e}")
    finally:
        # Ensure the database connection is closed
        db.close()

    return rows, RecordID


def update_reading_book_data(record_id, date_range):
    db = pymysql.connect(**conf)
    with db:
        with db.cursor() as c:
            try:
                c.execute(
                    "UPDATE `complete date estimates` SET EstimateDate = %s, EstimatedFinishDate = %s WHERE RecordID = %s",
                    (datetime.datetime.now(), date_range[0], record_id))
            except pymysql.Error as e:
                app_logger.error(e)
        db.commit()


def _estimate_values(x_values, y_values, target_x):
    """
    Estimates the minimum and maximum y-values for a given target x-value based on linear interpolation
    of the input x and y values.

    Parameters:
    - x_values (list or numpy array): The x-values of the data points.
    - y_values (list or numpy array): The y-values of the data points.
    - target_x (float): The x-value for which to estimate the corresponding y-value range.

    Returns:
    - list: A list containing the minimum and maximum estimated y-values for the target x-value.
    """
    slope, _ = np.polyfit(x_values, y_values, 1)  # linear fit to all points
    most_likely_y = slope * (target_x - np.max(x_values)) + np.max(y_values)
    estimated_range = [float('inf'), -float('inf')]
    for i in range(len(x_values) - 1):
        denom = x_values[i + 1] - x_values[i]
        if denom == 0:
            app_logger.error(f"Divide by zero error at index {i} -- skipping")
            app_logger.debug(f"Did you enter the same page count for two different days?")
            continue
        else:
            slope = (y_values[i + 1] - y_values[i]) / denom
        estimated_y = slope * (target_x - np.max(x_values)) + np.max(y_values)
        estimated_range[0] = min(estimated_range[0], estimated_y)
        estimated_range[1] = max(estimated_range[1], estimated_y)

    app_logger.debug(f"Estimated days: {most_likely_y} and estimated range: {estimated_range}")
    # expected, shortest, longest in days from first record
    return [int(x) for x in [most_likely_y, estimated_range[0], estimated_range[1]]]


def estimate_completion_dates(reading_data, total_pages):
    """
    Estimates the book completion date based on reading data and provides a range of potential completion dates.

    Parameters:
    - reading_data (list of lists): Each sublist contains [datetime object, pages read, day number].
    - start_date (datetime.date): The date when the reading started.
    - total_readable_pages (int): Total number of pages in the book.

    Returns:
    - datetime.date: The estimated date of completion.
    - tuple: A tuple containing the earliest and latest estimated completion dates as datetime.date objects.
    """

    start_date = reading_data[0][0]  # first record date
    # Convert input data to numpy arrays for manipulation
    data_array = np.array(reading_data)
    pages_read = np.array(data_array[:, 1], dtype=np.float64)  # Extract pages read
    day_number = np.array(data_array[:, 2], dtype=np.float64)  # Extract day numbers

    likely_days, min_days, max_days = _estimate_values(pages_read, day_number, total_pages)  # days from first record
    # Calculate the minimum and maximum estimated completion dates
    date_likely = start_date + datetime.timedelta(days=likely_days)
    est_date_min = start_date + datetime.timedelta(days=min_days)
    est_date_max = start_date + datetime.timedelta(days=max_days)

    return date_likely, est_date_min, est_date_max


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
    total_readable_pages = float(book_data[0][1])
    # Calculate the estimate date range
    estimate_date_range = estimate_completion_dates(reading_data, total_readable_pages)

    # Update the database with the estimated date range
    update_reading_book_data(record_id, estimate_date_range)

    # Format the estimated date range for output
    formatted_estimates = [date.strftime(FMT) for date in estimate_date_range]

    return formatted_estimates
