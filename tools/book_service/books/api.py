__version__ = '0.13.0'

from io import BytesIO
from logging.config import dictConfig

import pandas as pd
from flask import Flask, Response, request, send_file
from flask_cors import CORS
from matplotlib import pylab as plt

from api_util import *
from isbn_com import Endpoint as isbn

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
cors = CORS(app)


@app.route('/configuration')
@require_appkey
def configuration():
    rdata = json.dumps({
        "version": __version__,
        "configuration": conf,
        "isbn_configuration": isbn_conf,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# UI Utilities
##########################################################################

@app.route('/valid_locations')
def valid_locations():
    """
    Endpoint to retrieve distinct locations from the 'book collection' table.
    Returns a JSON response containing the locations.
    """
    db = None
    try:
        db = pymysql.connect(**conf)
        cursor = db.cursor()

        # Execute the query
        query = "SELECT DISTINCT Location FROM `book collection` ORDER by Location ASC;"
        app.logger.debug(query)
        cursor.execute(query)

        # Fetch and process the results
        locations = cursor.fetchall()
        locations_list = [loc[0] for loc in locations]
        sorted_locations_list = sort_by_indexes(locations_list, locations_sort_order)
        result = json.dumps({"header": "Location", "data": sorted_locations_list})

    except pymysql.Error as e:
        # Log and handle database errors
        app.logger.error(e)
        result = {"error": str(e)}
    finally:
        # Ensure the database connection is closed
        if db:
            db.close()

    # Return the successful response
    return Response(response=result, status=200, headers=resp_header(result))


##########################################################################
# RECENT UPDATES
##########################################################################


@app.route('/recent')
def recent():
    """
    Endpoint to retrieve ids and title of recently updated items
    Returns a JSON response containing the items.
    """
    db = None
    try:
        db = pymysql.connect(**conf)
        cursor = db.cursor()

        # Execute the query
        query = ('SELECT abc.BookCollectionID, max(abc.LastUpdate) as LastUpdate, bc.Title FROM\n'
                 '(       SELECT BookCollectionID, LastUpdate \n'
                 '        FROM `book collection`\n'
                 '        UNION\n'
                 '        SELECT BookCollectionID , LastUpdate \n'
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
                 'ORDER BY LastUpdate DESC LIMIT 10;\n')
        app.logger.debug(query)
        cursor.execute(query)

        # Fetch and process the results
        recent_books = []
        for a, b, c in cursor.fetchall():
            _date = b.strftime(FMT)
            _title = c if len(c) <= 43 else c[:40] + "..."
            recent_books.append([a, _date, _title])
        result = json.dumps({"header": ["BookCollectionID", "LastUpdate", "Title"], "data": recent_books})

    except pymysql.Error as e:
        # Log and handle database errors
        app.logger.error(e)
        result = {"error": str(e)}
    finally:
        # Ensure the database connection is closed
        if db:
            db.close()

    # Return the successful response
    return Response(response=result, status=200, headers=resp_header(result))


##########################################################################
# ADDS
##########################################################################

@app.route('/add_books', methods=['POST'])
@require_appkey
def add_books():
    """
    JSON Post Payload:
    [{
      "Title": "Delete Me Now",
      "Author": "Tester, N A",
      "CopyrightDate": "1999-01-01",
      "ISBNNumber": "1234",
      "ISBNNumber13": "1234",
      "PublisherName": "Printerman",
      "CoverType": "Hard",
      "Pages": "7",
      "Location": "Main Collection",
      "Note": "",
      "Recycled": 0
    }, ...]

    E.g.
    curl -X POST -H "Content-type: application/json" -d @./example_json_payloads/test_add_books.json \
    http://172.17.0.2:5000/add_books

    :return:
    """
    # records should be a list of dictionaries including all fields
    records = request.get_json()
    db = pymysql.connect(**conf)
    search_str = ("INSERT INTO `book collection` "
                  "(Title, Author, CopyrightDate, ISBNNumber, ISBNNumber13, PublisherName, CoverType, Pages, "
                  "Location, Note, Recycled) "
                  "VALUES "
                  "(\"{Title}\", \"{Author}\", \"{CopyrightDate}\", \"{ISBNNumber}\", \"{ISBNNumber13}\", "
                  "\"{PublisherName}\", \"{CoverType}\", \"{Pages}\", "
                  "\"{Location}\", \"{Note}\", \"{Recycled}\");")
    book_id_str = "SELECT LAST_INSERT_ID();"
    rdata = []
    with db:
        with db.cursor() as c:
            for record in records:
                try:
                    if len(record["CopyrightDate"].strip()) == 4:
                        record["CopyrightDate"] += "-01-01 00:00:00"  # make it a valid date string!
                    c.execute(search_str.format(**record))
                    c.execute(book_id_str)
                    record["BookCollectionID"] = c.fetchall()[0][0]
                    rdata.append(record)
                except pymysql.Error as e:
                    app.logger.error(e)
                    rdata.append({"error": str(e)})
        db.commit()
    rdata = json.dumps({"add_books": rdata})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/add_read_dates', methods=['POST'])
@require_appkey
def add_read_dates():
    """
    Post Payload:
    [{
      "BookCollectionID": 1606,
      "ReadDate": "0000-00-00",
      "ReadNote": ""
    }, ...]

    E.g.
    curl -X POST -H "Content-type: application/json" -d @./example_json_payloads/test_update_read_dates.json \
    http://172.17.0.2:5000/update_read_dates

    :return:
    """
    # records should be a list of dictionaries including all fields
    db = pymysql.connect(**conf)
    records = request.get_json()
    search_str = 'INSERT INTO `books read` (BookCollectionID, ReadDate, ReadNote) VALUES '
    search_str += '({BookCollectionID}, "{ReadDate}", "{ReadNote}")'
    res = {"update_read_dates": [], "error": []}
    with db:
        with db.cursor() as c:
            for record in records:
                try:
                    app.logger.debug(search_str.format(**record))
                    c.execute(search_str.format(**record))
                    res["update_read_dates"].append(record)
                except pymysql.Error as e:
                    app.logger.error(e)
                    res["error"].append(str(e))
        db.commit()
    res = json.dumps(res)
    response_headers = resp_header(res)
    return Response(response=res, status=200, headers=response_headers)


@app.route('/books_by_isbn', methods=['POST'])
@require_appkey
def books_by_isbn():
    """
    Creates records from isbn lookup and adds to the collection.

    curl -X POST http://192.168.127.7/books/books_by_isbn -H 'Content-type:application/json' -d '{"isbn_list":["0060929480"]}'

    Arguments
        List of isbns in isbn_list (strings) of the books you wish to get info
    Returns
        None or error
        bc.result is list of ids added.
    """
    book_isbn_list = request.get_json()["isbn_list"]
    res = []
    a = isbn(isbn_conf)
    for book_isbn in book_isbn_list:
        res_json = a.get_book_by_isbn(book_isbn)
        if res_json is not None:
            proto = a._endpoint_to_collection_db(res_json)
            res.append(proto)
        else:
            app.logger.error(f"No records found for isbn {book_isbn}.")
    rdata = json.dumps({"book_records": res})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# UPDATES
##########################################################################
@app.route('/update_edit_read_note', methods=['POST'])
@require_appkey
def update_edit_read_note():
    """
    Post Payload:
    {
      "BookCollectionID": 1606,
      "ReadDate": "0000-00-00"
      "ReadNote": "New note."
    }

    E.g.
    curl -X POST -H "Content-type: application/json" -d @./example_json_payloads/test_update_edit_read_note.json \
    http://172.17.0.2:5000/update_update_edit_read_note

    :return:
    """
    # records should be a single dictionaries including all fields
    db = pymysql.connect(**conf)
    record = request.get_json()
    search_str = "UPDATE `books read` SET "
    search_str += "ReadNote=\"{ReadNote}\" "
    search_str += "WHERE BookCollectionID = \"{BookCollectionID}\" AND ReadDate = \"{ReadDate}\";"
    app.logger.debug(search_str.format(**record))
    rdata = []
    with db:
        with db.cursor() as c:
            try:
                c.execute(search_str.format(**record))
                rdata.append(record)
            except pymysql.Error as e:
                app.logger.error(e)
                rdata.append({"error": str(e)})
        db.commit()
    rdata = json.dumps({"update_read": rdata})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/update_book_note_status', methods=['POST'])
@require_appkey
def update_book_note_status():
    """
    Post Payload:
    {
      "BookCollectionID": 1606,
      "Note": "",
      "Recycled": 0
    }

    E.g.
    curl -X POST -H "Content-type: application/json" -d @./example_json_payloads/test_update_book_note_status.json \
    http://172.17.0.2:5000/update_book_note_status

    :return:
    """
    # records should be a single dictionaries including all changed fields
    record = request.get_json()
    # test of the record has BookCollectionID and one or both of Note and Recycled fields
    if not ("BookCollectionID" in record and ("Note" in record or "Recycled" in record)):
        rdata = json.dumps({"error": "Missing required fields: BookCollectionID, Note OR Recycled"})
        response_headers = resp_header(rdata)
        return Response(response=rdata, status=400, headers=response_headers)
    else:
        data = update_book_record_by_key(record)
        rdata = json.dumps({"update_read": data})
        response_headers = resp_header(rdata)
        return Response(response=rdata, status=200, headers=response_headers)


@app.route('/update_book_record', methods=['POST'])
@require_appkey
def update_book_record():
    """
    Post Payload:
    {
      "BookCollectionID": 1606,
      "Recycled": 0
    }

    E.g.
    curl -X POST -H "Content-type: application/json" -d @./example_json_payloads/test_update_book_note_status.json \
    http://172.17.0.2:5000/update_book_record

    :return:
    """
    # records should be a single dictionaries including all changed fields
    record = request.get_json()
    # test of the record has BookCollectionID and one of any other field
    if not ("BookCollectionID" in record and len(record.keys()) > 1):
        rdata = json.dumps({"error": "Missing required fields: BookCollectionID, and any other field"})
        response_headers = resp_header(rdata)
        return Response(response=rdata, status=400, headers=response_headers)
    else:
        data = update_book_record_by_key(record)
        rdata = json.dumps({"update_read": data})
        response_headers = resp_header(rdata)
        return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# REPORTS
##########################################################################


@app.route('/summary_books_read_by_year')
@app.route('/summary_books_read_by_year/<target_year>')
def summary_books_read_by_year(target_year=None):
    rdata, _, _ = summary_books_read_by_year_utility(target_year)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/books_read')
@app.route('/books_read/<target_year>')
def books_read(target_year=None):
    rdata, _, _ = books_read_utility(target_year)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/status_read/<book_id>')
def status_read(book_id=None):
    db = pymysql.connect(**conf)
    search_str = (f"select BookCollectionID, ReadDate, ReadNote "
                  f"FROM `books read` "
                  f"WHERE BookCollectionID = {book_id} ORDER BY ReadDate ASC;")
    app.logger.debug(search_str)
    c = db.cursor()
    header = ["BookCollectionID", "ReadDate", "ReadNote"]
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app.logger.error(e)
        rdata = {"error": str(e)}
    else:
        s = c.fetchall()
        rdata = serialize_rows(s, header)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# SEARCH
##########################################################################

@app.route('/books_search')
def books_search():
    # process any query parameters
    db = pymysql.connect(**conf)
    args = request.args
    where = []
    for key in args:
        if key == "BookCollectionID":
            where.append(f"a.{key} = \"{args.get(key)}\"")
        elif key == "ReadDate":
            where.append(f"b.{key} LIKE \"%{args.get(key)}%\"")
        elif key == "Tags":
            _, s, _ = tags_search_utility(args.get(key))
            id_list = str(tuple([int(x[0]) for x in s]))
            if len(s) == 1:
                # remove trailing comma
                id_list = id_list.replace(",", "")
            app.logger.debug(id_list)
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
    app.logger.debug(search_str)
    header = table_header + ["ReadDate"]
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app.logger.error(e)
        rdata = json.dumps({"error": str(e)})
    else:
        s = c.fetchall()
        rdata = serialize_rows(s, header)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# TAGS
##########################################################################

@app.route('/add_tag/<book_id>/<tag>', methods=["put"])
@require_appkey
def add_tag(book_id, tag):
    db = pymysql.connect(**conf)
    tag = tag.lower()
    with db:
        with db.cursor() as c:
            try:
                c.execute(f'INSERT IGNORE INTO `tag labels` SET Label="{tag}";')
                c.execute(f'SELECT * from `tag labels` WHERE Label="{tag}";')
                tag_id = c.fetchall()[0][0]
                c.execute('INSERT INTO `books tags` (BookID, TagID) VALUES (%s, %s)', (book_id, tag_id))
                rdata = json.dumps({"BookID": f"{book_id}", "Tag": f"{tag}", "TagID": f"{tag_id}"})
            except pymysql.Error as e:
                app.logger.error(e)
                rdata = json.dumps({"error": str(e)})
        db.commit()
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/tag_counts')
@app.route('/tag_counts/<tag>')
def tag_counts(tag=None):
    db = pymysql.connect(**conf)
    search_str = "SELECT a.Label as Tag, COUNT(b.TagID) as Count"
    search_str += " FROM `tag labels` a JOIN `books tags` b ON a.TagID =b.TagID"
    if tag is not None:
        search_str += f" WHERE Label LIKE \"{tag}%\""
    search_str += " GROUP BY Label ORDER BY count DESC, Label ASC"
    app.logger.debug(search_str)
    header = ["Tag", "Count"]
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        rdata = json.dumps({"error": str(e)})
        app.logger.error(e)
    else:
        s = c.fetchall()
        rdata = serialize_rows(s, header)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/tags/<book_id>')
def tags(book_id=None):
    db = pymysql.connect(**conf)
    search_str = "SELECT a.Label as Tag"
    search_str += " FROM `tag labels` a JOIN `books tags` b ON a.TagID =b.TagID"
    search_str += f" WHERE b.BookID = {book_id} ORDER BY Tag"
    app.logger.debug(search_str)
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app.logger.error(e)
        rdata = {"error": str(e)}
    else:
        s = c.fetchall()
        tag_list = [x[0].strip() for x in s]
        s = list(s)
        rdata = json.dumps({"BookID": book_id, "tag_list": tag_list})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/update_tag_value/<current>/<updated>')
@require_appkey
def update_tag_value(current, updated):
    db = pymysql.connect(**conf)
    with db:
        with db.cursor() as c:
            try:
                _updated = updated.lower().strip(" ")
                records = c.execute("UPDATE `tag labels` SET Label = '{}' WHERE Label = '{}'".format(
                    _updated, current))
                rdata = json.dumps({"data": {"tag_update": f"{current} >> {updated}", "updated_tags": records}})
            except pymysql.Error as e:
                app.logger.error(e)
                rdata = json.dumps({"error": str(e)})
        db.commit()
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/tags_search/<match_str>')
def tags_search(match_str):
    rdata, s, header = tags_search_utility(match_str)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/tag_maintenance')
def tag_maintenance():
    db = pymysql.connect(**conf)
    rdata = {"tag_maintenance": {}}
    with db:
        with db.cursor() as c:
            try:
                # lower case
                c.execute("UPDATE `tag labels` SET Label = TRIM(LOWER(Label))")
                db.commit()
            except pymysql.Error as e:
                rdata = {"error": [str(e)]}
                app.logger.error(e)
    rdata = json.dumps(rdata)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# READING ESTIMATES
##########################################################################
@app.route('/date_page_records/<record_id>')
def date_page_records(record_id=None):
    # data is [(RecordDate, page, day_number from first page record), ...]
    data, record_id = daily_page_record_from_db(record_id)
    rdata = {"date_page_records": [], "RecordID": record_id}
    if len(data) > 0:
        rdata["date_page_records"] = [(x.strftime(FMT), int(y), int(z)) for [x, y, z] in data]
    else:
        rdata["error"] = "No records found."
    rdata = json.dumps(rdata)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/record_set/<book_id>')
def record_set(book_id=None):
    db = pymysql.connect(**conf)
    rdata = {"record_set": {"BookCollectionID": book_id, "RecordID": [], "Estimate": []}}
    q = ("SELECT StartDate, RecordID FROM `complete date estimates` "
         f"WHERE BookCollectionID = {book_id} ORDER BY StartDate ASC")
    with db:
        with db.cursor() as c:
            try:
                c.execute(q)
                res = c.fetchall()
            except pymysql.Error as e:
                rdata["error"].append(str(e))
                app.logger.error(e)
        db.commit()
    for record in [(str(x[0]), int(x[1])) for x in res]:
        rdata["record_set"]["RecordID"].append(record)
        rdata["record_set"]["Estimate"].append(calculate_estimates(record[1]))
    rdata = json.dumps(rdata)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/add_date_page', methods=['POST'])
@require_appkey
def add_date_page():
    """
    Post Payload:
    {
      "RecordID": 123,
      "RecordDate": "0000-00-00"
      "Page": 123
    }

    E.g.
    curl -X POST -H "Content-type: application/json" -d @./example_json_payloads/test_add_date_page.json \
    http://172.17.0.2:5000/add_date_page

    :return:
    """
    # records should be a single dictionaries including all fields
    record = request.get_json()
    search_str = "INSERT INTO `daily page records` SET "
    search_str += 'RecordID="{RecordID}", '
    search_str += 'RecordDate="{RecordDate}", '
    search_str += 'page="{Page}";'
    app.logger.debug(search_str.format(**record))
    db = pymysql.connect(**conf)
    rdata = json.dumps({"error": "No record added."})
    with db:
        with db.cursor() as c:
            try:
                c.execute(search_str.format(**record))
                rdata = json.dumps({"add_date_page": record})
            except pymysql.Error as e:
                app.logger.error(e)
                rdata = json.dumps({"add_date_page": {}, "error": str(e)})
        db.commit()
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/add_book_estimate/<book_id>/<last_readable_page>', methods=["PUT"])
@app.route('/add_book_estimate/<book_id>/<last_readable_page>/<start_date>', methods=["PUT"])
@require_appkey
def add_book_estimate(book_id, last_readable_page, start_date=None):
    # TODO: if you call it again, you get a new record_id for a second reading of the same book
    db = pymysql.connect(**conf)
    last_readable_page = int(last_readable_page)
    if start_date is None:
        start_date = datetime.datetime.now().strftime(FMT)
    q = (f'INSERT INTO `complete date estimates` SET BookCollectionID={book_id},'
         f' StartDate="{start_date}", LastReadablePage={last_readable_page};')
    app.logger.debug(q)
    with db:
        with db.cursor() as c:
            try:
                c.execute(q)
                rdata = json.dumps({"add_book_estimate":
                                        {"BookCollectionID": f"{book_id}", "LastReadablePage":
                                            f"{last_readable_page}", "StartDate": f"{start_date}"}})
            except pymysql.Error as e:
                app.logger.error(e)
                rdata = json.dumps({"add_book_estimate": {}, "error": str(e)})
        db.commit()
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# IMAGES
##########################################################################
@app.route("/image/year_progress_comparison.png")
@app.route("/image/year_progress_comparison.png/<window>")
def year_progress_comparison(window=15):
    window = int(window)
    img = BytesIO()
    _, s, h = books_read_utility()
    df1 = pd.DataFrame(s, columns=h)
    df1 = df1.set_index("ReadDate")
    df1.index = pd.to_datetime(df1.index)
    df1 = df1.groupby(df1.index.to_period('Y'))['Pages'].apply(lambda x: x.cumsum())
    df1 = df1.reset_index()
    df1["Day"] = df1.ReadDate.apply(lambda x: x.dayofyear)
    df1["Year"] = df1.ReadDate.apply(lambda x: x.year)
    fig_size = [8, 8]
    xlim = [0, 365]
    ylim = [0, max(df1.Pages)]
    years = df1.Year.unique()[-window:].tolist()
    current_year = max(years)
    y = years.pop(0)
    _df = df1.loc[df1.Year == y]
    ax = _df.plot("Day", "Pages", figsize=fig_size, xlim=xlim, ylim=ylim, label=y)
    for y in years:
        _df = df1.loc[df1.Year == y]
        lw = 1 if y != current_year else 4
        ax = _df.plot("Day", "Pages", figsize=fig_size, xlim=xlim, ylim=ylim, ax=ax, label=y, lw=lw)
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route("/image/all_years.png")
@app.route("/image/all_years.png/<year>")
def all_years(year=None):
    if year is None:
        year = datetime.datetime.now().year
    else:
        year = int(year)
    img = BytesIO()
    _, s, h = summary_books_read_by_year_utility()
    df = pd.DataFrame(s, columns=h)
    df['pages read'] = df['pages read'].astype(float)
    df["rank"] = df["pages read"].rank(ascending=False)
    df.sort_values(by=["rank"], inplace=True)
    df.reset_index()
    # When we are in a new year, but no read books yet, we need to add the year
    if year not in df.year.unique():
        year = df.year.unique().max()
    now_df = df.loc[df["year"] == year]
    app.logger.debug(now_df)
    fig, axs = plt.subplots(3, 1, figsize=[10, 18])
    df.hist("pages read", bins=14, color="darkblue", ax=axs[0])
    axs[0].axvline(x=int(now_df["pages read"].iloc[0]), color="red")
    df.plot.bar(x="rank", y="pages read", width=.95, color="darkblue", ax=axs[1])
    axs[1].axvline(x=int(now_df["rank"].iloc[0]) - 1, color="red")
    df.sort_values("year").plot.bar(x="year", y="pages read", width=.95, color="darkblue", ax=axs[2])
    fig.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
