import datetime
import functools
import json
import logging
from decimal import Decimal

import numpy as np
import pymysql
from flask import request, abort

app_logger = logging.getLogger(__name__)

table_header = ["BookCollectionID",
                "Title",
                "Author",
                "CopyrightDate",
                "ISBNNumber",
                "PublisherName",
                "CoverType",
                "Pages",
                "Category",
                "Note",
                "Recycled",
                "Location",
                "ISBNNumber13"]

locations_sort_order = [3, 4, 2, 1, 7, 6, 5]

FMT = "%Y-%m-%d"

API_KEY = None


def read_json_configuration():
    """
    Retrieve database and ISBN lookup configuration from JSON file.

    Parameters
    ----------
    None

    Returns
    -------
    tuple
        A tuple containing two dictionaries:
        * ``books_db_config`` – mapping database connection parameters
        * ``isbn_lookup_config`` – mapping ISBN lookup service parameters
        The global variable ``API_KEY`` is set during execution.

    Raises
    ------
    SystemExit
        If a configuration key is missing or the file cannot be read.

    Notes
    -----
    The function reads ``./config/configuration.json`` and expects the following
    keys: ``username``, ``password``, ``database``, ``host``, ``port``,
    ``isbn_com.url_isbn``, ``isbn_com.key`` and ``api_key``.  If any key is
    absent a ``SystemExit`` exception is raised and the error is logged.
    """
    config_filename = "./config/configuration.json"
    with open(config_filename, "r") as config_file:
        c = json.load(config_file)
        try:
            books_db_config = {
                "user": c["username"].strip(),
                "passwd": c["password"].strip(),
                "db": c["database"].strip(),
                "host": c["host"].strip(),
                "port": int(c["port"])
            }
            isbn_lookup_config = {
                "url_isbn": c["isbn_com"]["url_isbn"].strip(),
                "key": c["isbn_com"]["key"].strip()
            }
            global API_KEY
            API_KEY = c["api_key"].replace('\n', '')
        except KeyError as e:
            app_logger.error(e)
            raise SystemExit("Missing configuration file.")
        return books_db_config, isbn_lookup_config


# server configuration
books_conf, isbn_conf = read_json_configuration()


def sort_list_by_index_list(lst, indexes, reverse=False):
    """
    Sort elements of a list based on a corresponding list of indexes.

    This function pairs each element of `lst` with an index from `indexes`,
    sorts the pairs by the indexes, and then returns a new list containing
    the elements in that sorted order. An optional `reverse` flag can be
    used to reverse the order of the sorting.

    Parameters
    ----------
    lst : list
        The list of values to be reordered.
    indexes : list
        The list of indexes that determine the sorting order.
    reverse : bool, optional
        If True, the sorting order is reversed.

    Returns
    -------
    list
        A list of values from `lst` sorted according to `indexes`.
    """
    return [val for (_, val) in sorted(zip(indexes, lst), key=lambda x: \
        x[0], reverse=reverse)]


def require_app_key(view_function):
    """
    Verify that an incoming HTTP request contains a valid API key before executing
    the wrapped view function.

    Parameters
    ----------
    view_function : callable
        The view function to be protected. It will be called with the same
        positional and keyword arguments that the decorated function receives.

    Returns
    -------
    callable
        A new function that first checks the request header 'x-api-key' against
        the configured API_KEY. If the key matches, it forwards the call to
        view_function; otherwise it logs an error and aborts with a 401
        Unauthorized response.

    Raises
    ------
    HTTPException
        Raised when the 'x-api-key' header is missing or does not match
        the expected API_KEY. The abort(401) call from Flask triggers this
        exception, causing an HTTP 401 Unauthorized error to be returned.
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


def serialized_result_dict(db_result_rows, header=None, error_list=None):
    """
    Serializes database result rows into JSON.

    This function takes the result rows from a database query, optionally a
    header specifying column names, and an optional list of error messages.
    It first converts the rows into a dictionary representation by delegating
    to `create_result_dict`.  The resulting dictionary is then encoded as a
    JSON string using the standard library `json.dumps` function.  The JSON
    string is returned to the caller.

    Arguments
    ---------
    db_result_rows
        The rows returned from a database query, typically a list of tuples
        or lists.
    header
        Optional list of column names that map to each element of a row.
        If omitted, the keys in the resulting dictionary are generated
        automatically.
    error_list
        Optional list of error messages to include in the output dictionary.

    Returns
    -------
    str
        A JSON formatted string representing the serialized result set.

    Raises
    ------
    ValueError
        If `create_result_dict` raises a `ValueError` when converting the rows.
    TypeError
        If `json.dumps` receives an unsupported object type.

    Notes
    -----
    The function does not perform any validation of the input beyond what
    `create_result_dict` and `json.dumps` require.  It is intended for
    serialization tasks where the output will be transmitted or stored as
    text.  The caller should ensure that the database rows and header are
    consistent in length.

    See Also
    --------
    create_result_dict
        Helper function that creates the intermediate dictionary from the rows.
    json.dumps
        Standard library function used for JSON encoding.
    """
    result = _create_serializeable_result_dict(db_result_rows, header, error_list=None)
    result_dict_json = json.dumps(result)
    return result_dict_json


def _convert_db_types(value_list):
    """
    Converts database row values to JSON‑serializable types.

    When data is fetched from a database, certain Python types such as
    `Decimal`, `datetime.datetime` and `datetime.date` are not directly
    serializable by many JSON libraries.  This helper function transforms a
    sequence of values by converting each `Decimal` to a `float` and each
    date‑time object to a string formatted as ``YYYY‑MM‑DD``.  All other
    values are passed through unchanged.  The original list is left
    untouched; a new list is returned.

    Args:
        value_list: The list of values to be converted.  Elements may be
            of type `Decimal`, `datetime.datetime`, `datetime.date`, or
            other scalar types such as `int`, `float`, or `str`.

    Returns:
        A new list where each `Decimal` has been converted to a `float`,
        each `datetime.datetime` or `datetime.date` has been formatted
        as a string in the ``YYYY‑MM‑DD`` format, and all other values
        are left unchanged.
    """
    new_value_list = []
    for d in value_list:  # Process each value in the row
        if isinstance(d, Decimal):  # Convert Decimal values to float
            new_value_list.append(float(d))
        elif isinstance(d, datetime.datetime) or isinstance(d, datetime.date):  # Format dates
            new_value_list.append(d.strftime("%Y-%m-%d"))
        else:  # Include other values as-is
            new_value_list.append(d)
    return new_value_list


def _create_serializeable_result_dict(db_result, header, error_list=None):
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
            ],
            "error": ["error string"]   # This key is optional
        }
        - Decimal values are converted to floats.
        - datetime.date and datetime.datetime values are formatted as "YYYY-MM-DD".
        - Other values are included as-is.

    Notes:
    - If the length of the header does not match the length of a row, a warning message
      is printed to the console.
    """
    result_dict = {"header": header, "data": []}  # Initialize the result dictionary
    if error_list is not None:
        # optional the include error key
        result_dict["error"] = error_list

    result_rows = []  # List to store processed rows
    if db_result is None or len(db_result) == 0:
        pass
    elif isinstance(db_result[0], tuple) or isinstance(db_result[0], list):
        # Standard format for multiple columns
        for row in db_result:  # Iterate over each row in the cursor
            if len(header) != len(row):  # Check if the header length matches the row length
                app_logger.debug("mismatched header to data provided")
            result_rows.append(_convert_db_types(row))  # Add the processed row to the result rows list
    else:  # Non-standard format for single column as a list
        result_rows = _convert_db_types(db_result)
    result_dict["data"] = result_rows  # Add the processed rows to the result dictionary
    return result_dict  # Return the result dictionary


def resp_header(rdata):
    """
    Generate HTTP response headers for a JSON payload.

    This function constructs a list of header tuples suitable for sending an HTTP
    response containing JSON data.  It automatically sets the `Content-Type`
    to JSON with UTF‑8 encoding and calculates the correct `Content-Length`
    based on the supplied response body.

    Args:
        rdata (bytes or str): The raw response body.  The length of this data is
            used to set the `Content-Length` header.  `rdata` should already be
            encoded as UTF‑8 bytes or a Unicode string representing the JSON
            payload.

    Returns:
        list[tuple[str, str]]: A list of two‑item tuples where each tuple
            contains a header name and its corresponding value.  The list
            always contains the `Content-Type` header for JSON with UTF‑8
            encoding followed by the `Content-Length` header reflecting
            the byte length of `rdata`.
    """
    response_header = [
        ('Content-type', 'application/json; charset=utf-8'),
        ('Content-Length', str(len(rdata)))
    ]
    return response_header


##########################################################################
# BASIC API UTILITIES
#    Return: data_rowe, raw_data, header, error_str_list
##########################################################################

def get_valid_locations():
    """
    Retrieves a sorted list of distinct locations from the book collection table.

    The function connects to the MySQL database, executes a query to obtain unique
    location values, and returns them in a sorted order according to a predefined
    sort index. It also provides the raw query results and a list of column names,
    along with any error messages that may have occurred during the database
    operation.

    Args:
        None

    Returns:
        tuple[list[str], tuple[tuple[str, ...], ...], list[str], list[str] | None]
            A 4‑tuple containing:
            - ``sorted_locations_list`` – the locations sorted according to
              ``locations_sort_order``.
            - ``locations`` – the raw ``SELECT`` result set as returned by
              ``fetchall()``.
            - ``["Location"]`` – a single‑element list of column names.
            - ``error_list`` – a list containing the string representation of any
              database error that was caught, or ``None`` if no error occurred.
    """
    db = None
    error_list = None
    try:
        db = pymysql.connect(**books_conf)
        cursor = db.cursor()

        # Execute the query
        query = "SELECT DISTINCT Location FROM `book collection` ORDER by Location ASC;"
        app_logger.debug(query)
        cursor.execute(query)

        # Fetch and process the results
        locations = cursor.fetchall()
        locations_list = [loc[0] for loc in locations]
        sorted_locations_list = sort_list_by_index_list(locations_list, locations_sort_order)
    except pymysql.Error as e:
        # Log and handle database errors
        app_logger.error(e)
        error_list = [str(e)]
    finally:
        # Ensure the database connection is closed
        if db:
            db.close()
    return sorted_locations_list, locations, ["Location"], error_list


def get_recently_touched(limit=10):
    """
    Retrieve a list of recently touched book collections.

    This function queries the database to find the most recently updated
    book collections, combining data from several tables.  It returns the
    results together with the raw database rows, a header describing the
    columns, and any error messages that occurred during execution.

    Parameters
    ----------
    limit : int, optional
        The maximum number of records to return. Defaults to 10.

    Returns
    -------
    tuple
        A 4‑tuple containing:

        * recent_books (list[list]): A list where each element is a list of
          three items: ``BookCollectionID`` (int), ``LastUpdate`` (str or
          None), and ``Title`` (str). ``LastUpdate`` is formatted according
          to the global ``FMT`` constant; titles longer than 43 characters
          are truncated to 40 characters followed by ellipsis.

        * s (tuple): The raw rows returned by the cursor's ``fetchall``.
          Each row is a tuple of the original column values.

        * header (list[str]): A list of column names used for the result
          set: ``["BookCollectionID", "LastUpdate", "Title"]``.

        * error_list (list[str] | None): A list containing a single error
          message if a ``pymysql.Error`` was raised; otherwise ``None``.

    Raises
    ------
    None
    """
    error_list = None
    db = None
    recent_books = []
    header = ["BookCollectionID", "LastUpdate", "Title"]
    s = None

    try:
        db = pymysql.connect(**books_conf)
        cursor = db.cursor()

        # Execute the query - removed duplicate UNION of book collection table
        query = ('SELECT abc.BookCollectionID, max(abc.LastUpdate) as LastUpdate, bc.Title FROM\n'
                 '(       SELECT BookCollectionID, LastUpdate \n'
                 '        FROM `book collection`\n'
                 '        UNION \n'
                 '        SELECT BookID as BookCollectionID, LastUpdate\n'
                 '        FROM `books tags`\n'
                 '        UNION\n'
                 '        SELECT a.BookCollectionID, b.LastUpdate\n'
                 '        FROM `complete date estimates` a JOIN `daily page records` b ON\n'
                 '        a.RecordID = b.RecordID\n'
                 '        UNION \n'
                 '        SELECT BookCollectionID, EstimateDate as LastUpdate\n'
                 '        FROM `complete date estimates`) abc\n'
                 'JOIN `book collection` bc ON abc.BookCollectionID = bc.BookCollectionID \n'
                 'GROUP BY abc.BookCollectionID, bc.Title\n'
                 'ORDER BY LastUpdate DESC LIMIT %s;\n')
        app_logger.debug(query)
        cursor.execute(query, (limit,))

        # Fetch and process the results
        s = cursor.fetchall()
        for a, b, c in s:
            _date = b.strftime(FMT) if b else None
            _title = c if len(c) <= 43 else c[:40] + "..."
            recent_books.append([a, _date, _title])

    except pymysql.Error as e:
        # Log and handle database errors
        app_logger.error(e)
        error_list = [str(e)]
    finally:
        # Ensure the database connection is closed
        if db:
            db.close()

    return recent_books, s, header, error_list


##########################################################################
# BOOKS WINDOW
##########################################################################

def get_next_book_id(current_book_id, direction=1):
    """
    Gets the next book collection ID in the database.

    Summary:
        Retrieves the next BookCollectionID from the `book collection` table in
        the MySQL database. The function uses the current ID and a direction
        flag to determine whether to look forward or backward. When the search
        reaches the end of the table it wraps around to the first or last
        entry, depending on the direction.

    Parameters:
        current_book_id (int): The current book collection identifier.
        direction (int, optional): A positive value indicates forward
            searching; a negative value indicates backward searching.
            Defaults to 1.

    Returns:
        int or None: The next book collection ID, or None if a database
        error occurs.

    Raises:
        pymysql.Error: If an error occurs during the database query.
    """
    db = pymysql.connect(**books_conf)
    order = "ASC" if direction > 0 else "DESC"
    ineq = ">" if direction > 0 else "<"
    query_str = ("SELECT a.BookCollectionID "
                 "FROM `book collection` as a "
                 f"WHERE a.BookCollectionID {ineq} {current_book_id} "
                 f"ORDER BY a.BookCollectionID {order} "
                 "LIMIT 1;")
    app_logger.debug(query_str)
    next_book_id = None
    c = db.cursor()
    try:
        c.execute(query_str)
    except pymysql.Error as e:
        app_logger.error(e)
        return next_book_id
    else:
        s = c.fetchall()
        # If no results, wrap around
        if len(s) == 0:
            if direction > 0:
                # get the first record
                next_book_id = 2
            else:
                query_str = ("SELECT max(a.BookCollectionID) "
                             "FROM `book collection` as a; ")
                c = db.cursor()
                try:
                    c.execute(query_str)
                except pymysql.Error as e:
                    app_logger.error(e)
                else:
                    s = c.fetchall()
                    next_book_id = s[0][0]
        else:
            next_book_id = s[0][0]
        return next_book_id


def get_book_ids_in_window(book_id, window):
    """
    Get a list of book IDs within a given window around a specific book ID.

    This function connects to a MySQL database and retrieves a contiguous block of
    book IDs that surrounds the supplied `book_id`. The window is divided into a
    top and bottom half.  If the requested range extends beyond the existing
    records, the function wraps around to the beginning or end of the collection
    to fill the deficit, ensuring the returned list has exactly `window`
    entries.

    Parameters
    ----------
    book_id : int
        The ID of the book around which the window is calculated.
    window : int
        The total number of book IDs to return, including the supplied
        `book_id`.

    Returns
    -------
    list[int]
        A list of book IDs ordered such that the supplied `book_id` is
        positioned near the center of the list.  The list length is equal to
        `window`.  If the underlying collection contains fewer records
        than requested, duplicates are inserted to satisfy the size.

    Raises
    ------
    pymysql.Error
        If a database query fails, the exception is logged but not
        propagated; the function continues with whatever results were
        retrieved so far.
    """
    db = pymysql.connect(**books_conf)
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


def get_complete_book_record(book_id):
    # process any query parameters
    db = pymysql.connect(**books_conf)
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
        result_data["book"] = _create_serializeable_result_dict(s, h_book)
    try:
        c.execute(q_read)
    except pymysql.Error as e:
        app_logger.error(e)
        result_data["error"].append(str(e))
    else:
        s = c.fetchall()
        result_data["reads"] = _create_serializeable_result_dict(s, h_read)
    try:
        c.execute(q_tags)
    except pymysql.Error as e:
        app_logger.error(e)
        result_data["error"].append(str(e))
    else:
        s = c.fetchall()
        result_data["tags"] = _create_serializeable_result_dict([[x[0] for x in s]], h_tags)

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
    db = pymysql.connect(**books_conf)
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
    error_list = None
    # Initialize database connection
    db = pymysql.connect(**books_conf)
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
    except pymysql.Error as e:
        app_logger.error(e)
        error_list = [str(e)]
        results = None
    finally:
        # Close the database connection
        db.close()

    return results, results, headers, error_list


def books_read_by_year_utility(target_year=None):
    """
    Retrieves books that have been read from the database, optionally filtered by a
    specific year.

    This function connects to a MySQL database using the connection parameters
    defined in ``books_conf``. It builds a SQL query that joins the
    ``book collection`` table with the ``books read`` table to fetch details for
    every book that has a non‑null ``ReadDate``.  If ``target_year`` is supplied,
    the query is restricted to entries whose ``ReadDate`` falls within that
    year.  The result set is returned together with a header list that
    contains column names and any error messages that occurred during query
    execution.

    Parameters
    ----------
    target_year : int, optional
        When supplied, only books whose ``ReadDate`` year matches
        ``target_year`` are returned.  If ``None`` (the default), all
        records with a non‑null ``ReadDate`` are included.

    Returns
    -------
    tuple
        * ``rows`` – A sequence of tuples, each representing a record
          returned by the query.  ``None`` if the query failed.
        * ``rows`` – The same sequence of tuples as the first element; kept
          for backward compatibility.
        * ``header`` – A list of column names for the result set.
        * ``error_list`` – A list containing an error message string if a
          database error was raised, otherwise ``None``.

    Raises
    ------
    pymysql.Error
        If the SQL execution fails, the exception is logged and the error
        message is stored in ``error_list``; the exception itself is not
        propagated.

    Notes
    -----
    The function logs the executed query using ``app_logger.debug``.  It is
    intended for internal use by other modules that require a list of books
    that have been read, possibly grouped by year.  The returned ``rows`` can
    be passed directly to functions that format the data for presentation
    or further analysis.
    """
    error_list = None
    db = pymysql.connect(**books_conf)
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
        error_list = [str(e)]
    else:
        s = c.fetchall()
    return s, s, header, error_list


def status_read_utility(book_id):
    """
    Retrieve the read status for a specified book from the database.

    Args:
        book_id (int): The ID of the book to query.

    Returns:
        tuple: A 4‑tuple with the following items:
            - s (list): The rows fetched from the query.
            - s (list): The same list of rows (duplicated in the original implementation).
            - header (list): The column names of the result set.
            - error_list (list or None): A list containing any error messages that
              occurred during execution, or ``None`` if the query succeeded.

    Notes:
        This function opens a connection to the MySQL database using the global
        ``books_conf`` configuration. It logs the SQL query for debugging purposes,
        executes the query, and captures any ``pymysql.Error`` exceptions.
        The database cursor is not closed explicitly; it relies on garbage
        collection for cleanup.
    """
    error_list = None
    db = pymysql.connect(**books_conf)
    search_str = (f"select BookCollectionID, ReadDate, ReadNote "
                  f"FROM `books read` "
                  f"WHERE BookCollectionID = {book_id} ORDER BY ReadDate ASC;")
    app_logger.debug(search_str)
    c = db.cursor()
    header = ["BookCollectionID", "ReadDate", "ReadNote"]
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app_logger.error(e)
        error_list = [str(e)]
    else:
        s = c.fetchall()
    return s, s, header, error_list


def tags_search_utility(match_str):
    match_str = match_str.lower().strip()
    error_list = None
    db = pymysql.connect(**books_conf)
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
        error_list = [str(e)]
    else:
        s = c.fetchall()
    return s, s, header, error_list


def books_search_utility(args):
    """
    This function searches a book collection database for records matching the provided criteria.

    The function builds a SQL query dynamically based on the keys in the `args` dictionary.  Certain keys are treated specially – for example, a key of `"BookCollectionID"` is matched exactly, while `"ReadDate"` is matched using a `LIKE` pattern.  The `"Tags"` key triggers a call to `tags_search_utility`, converting a list of tag identifiers into a tuple used in a sub‑query.  All other keys are compared using a `LIKE` clause.

    The query joins the `book collection` table with the `books read` table.  If any conditions are supplied, they are added to a `WHERE` clause; the results are ordered by author and title.  The function logs the final query for debugging purposes.

    After executing the query, the function fetches all rows and returns them along with a header list and any error information that may have been captured.

    Parameters
    ----------
    args : dict
        A dictionary of search criteria.  Keys correspond to column names in the
        book collection tables.  The following keys are handled specially:

        * ``BookCollectionID`` – exact match on the collection ID.
        * ``ReadDate`` – matched using a ``LIKE`` pattern.
        * ``Tags`` – the value is passed to ``tags_search_utility``; the resulting
          tag IDs are used to filter the collection IDs.
        * All other keys – matched using a ``LIKE`` pattern against the column
          of the same name in the ``book collection`` table.

    Returns
    -------
    tuple
        A four‑tuple containing:

        * ``s`` – the list of rows returned by the database query (each row is a
          tuple of column values).
        * ``s`` – the same list of rows returned again (this duplication is
          intentional to match the original return signature).
        * ``header`` – a list of column names for the result set, including the
          ``ReadDate`` column appended to the global ``table_header``.
        * ``error_list`` – a list containing any database error messages that
          occurred during query execution, or ``None`` if no errors were
          encountered.

    Notes
    -----
    * The function relies on several global objects: ``books_conf`` for the
      database connection parameters, ``tags_search_utility`` for resolving tag
      IDs, ``app_logger`` for logging, and ``table_header`` for header
      construction.  These objects must be defined in the module before calling
      this function.

    * Because the query is built by interpolating values directly into the SQL
      string, it is susceptible to SQL injection if ``args`` contains untrusted
      data.  Ensure that all values in ``args`` are sanitized before use.

    * The returned list of rows is fetched using the ``fetchall`` method of a
      MySQL cursor, which yields a list of tuples.  The column order matches the
      selection in the query string.
    """
    error_list = None
    s = None
    db = pymysql.connect(**books_conf)
    where = []
    for key in args:
        if key == "BookCollectionID":
            where.append(f"a.{key} = \"{args.get(key)}\"")
        elif key == "ReadDate":
            where.append(f"b.{key} LIKE \"%{args.get(key)}%\"")
        elif key == "Tags":
            _, s, _, _ = tags_search_utility(args.get(key))
            id_list = str(tuple([int(x[0]) for x in s]))
            if len(s) == 1:
                # remove trailing comma
                id_list = id_list.replace(",", "")
            app_logger.debug(id_list)
            where.append(f"a.BookCollectionID in {id_list}")
        else:
            where.append(f"a.{key} LIKE \"%{args.get(key)}%\"")
    where_str = " AND ".join(where)
    search_str = ("SELECT a.BookCollectionID, a.Title, a.Author, a.CopyrightDate, "
                  "a.ISBNNumber, a.PublisherName, a.CoverType, a.Pages, "
                  "a.Category, a.Note, a.Recycled, a.Location, a.ISBNNumber13, "
                  "b.ReadDate "
                  "FROM `book collection` as a LEFT JOIN `books read` as b "
                  "ON a.BookCollectionID = b.BookCollectionID ")
    if where_str != '':
        search_str += "WHERE " + where_str
    search_str += " ORDER BY a.Author, a.Title ASC"
    app_logger.debug(search_str)
    header = table_header + ["ReadDate"]
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app_logger.error(e)
        error_list = [str(e)]
    else:
        s = c.fetchall()
    return s, s, header, error_list


def book_tags(book_id):
    error_list = None
    s = None
    db = pymysql.connect(**books_conf)
    search_str = "SELECT a.Label as Tag"
    search_str += " FROM `tag labels` a JOIN `books tags` b ON a.TagID =b.TagID"
    search_str += f" WHERE b.BookID = {book_id} ORDER BY Tag"
    app_logger.debug(search_str)
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app_logger.error(e)
        error_list = [str(e)]
    else:
        s = c.fetchall()
        tag_list = [x[0].strip() for x in s]
        rdata = {"BookID": book_id, "tag_list": tag_list}
    return rdata, error_list


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
        db = pymysql.connect(**books_conf)
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
        db = pymysql.connect(**books_conf)
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
    result = {}
    db = pymysql.connect(**books_conf)
    with db:
        with db.cursor() as c:
            try:
                c.execute(
                    "UPDATE `complete date estimates` SET EstimateDate = %s, EstimatedFinishDate = %s WHERE RecordID = %s",
                    (datetime.datetime.now(), date_range[0], record_id))
            except pymysql.Error as e:
                app_logger.error(e)
                result = {"error": [str(e)]}
        db.commit()
    return result


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
    result = update_reading_book_data(record_id, estimate_date_range)
    if "error" in result:
        return [f'book reading data failure: {result["error"]}', None, None]

    # Format the estimated date range for output
    formatted_estimates = [date.strftime(FMT) for date in estimate_date_range]

    return formatted_estimates
