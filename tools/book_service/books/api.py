__version__ = '0.7.5'

from flask import Flask, Response, request, send_file
from io import BytesIO
import pandas as pd
from matplotlib import pylab as plt
from flask_cors import CORS
import pymysql

from api_util import *
from isbn_com.api import Endpoint as isbn

# server configuration
conf = get_configuration()
from logging.config import dictConfig

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
def configuration():
    rdata = json.dumps({
        "version": __version__,
        "configuration": conf,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# ADDS
##########################################################################

@app.route('/add_books', methods=['POST'])
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
    curl -X POST -H "Content-type: application/json" -d @./examples/test_add_books.json \
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
def add_read_dates():
    """
    Post Payload:
    [{
      "BookCollectionID": 1606,
      "ReadDate": "0000-00-00",
      "ReadNote": ""
    }, ...]

    E.g.
    curl -X POST -H "Content-type: application/json" -d @./examples/test_update_read_dates.json \
    http://172.17.0.2:5000/update_read_dates

    :return:
    """
    # records should be a list of dictionaries including all fields
    db = pymysql.connect(**conf)
    records = request.get_json()
    search_str = "INSERT INTO `books read` (BookCollectionID, ReadDate, ReadNote) VALUES "
    search_str += "({BookCollectionID}, \"{ReadDate}\", \"{ReadNote}\")"
    rdata = []
    with db:
        with db.cursor() as c:
            for record in records:
                try:
                    r = c.execute(search_str.format(**record))
                    rdata.append(record)
                except pymysql.Error as e:
                    app.logger.error(e)
                    rdata.append({"error": str(e)})
        db.commit()
    rdata = json.dumps({"update_read_dates": rdata})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/add_books_by_isbn', methods=['POST'])
def add_books_by_isbn(self, book_isbn_list):
    """
    Creates records from isbn lookup and adds to the collection.
    Arguments
        List of isbns (strings) of the books you wish to add to the collection. Required.
    Returns
        None or error
        bc.result is list of ids added.
    """
    db = pymysql.connect(**conf)
    book_isbn_list = request.get_json()["isbn_list"]
    res = []
    a = isbn()
    for book_isbn in book_isbn_list:
        res_json = a.get_book_by_isbn(book_isbn)
        if res_json is not None:
            proto = self._endpoint_to_collection_db(res_json)
            proto = self._inputer(proto)
            records = [proto]
            self.result = proto
            res.append(self._add_books(records))
        else:
            app.logger.error(f"No records found for isbn {book_isbn}.")
    rdata = json.dumps({"book_records": res})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# UPDATES
##########################################################################
@app.route('/update_edit_read_note', methods=['POST'])
def update_edit_read_note():
    """
    Post Payload:
    {
      "BookCollectionID": 1606,
      "ReadDate": "0000-00-00"
      "ReadNote": "New note."
    }

    E.g.
    curl -X POST -H "Content-type: application/json" -d @./examples/test_update_edit_read_note.json \
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
def update_book_note_status():
    """
    Post Payload:
    {
      "BookCollectionID": 1606,
      "Note": "",
      "Recycled": 0
    }

    E.g.
    curl -X POST -H "Content-type: application/json" -d @./examples/test_update_book_note_status.json \
    http://172.17.0.2:5000/update_book_note_status

    :return:
    """
    # records should be a single dictionaries including all fields
    db = pymysql.connect(**conf)
    record = request.get_json()
    search_str = "UPDATE `book collection` SET "
    continuation = False
    for key in record:
        if key == "BookCollectionID":
            continue
        if continuation:
            search_str += ", "
        else:
            continuation = True
        search_str += f" {key} = \"{record[key]}\""
    search_str += " WHERE BookCollectionID = {BookCollectionID} "
    app.logger.debug(search_str)
    rdata = []
    with db:
        with db.cursor() as c:
            try:
                c.execute(search_str.format(**record))
                app.logger.debug(search_str.format(**record))
                rdata.append(record)
            except pymysql.Error as e:
                app.logger.error(e)
                rdata.append({"error": str(e)})
        db.commit()
    rdata = json.dumps({"update_book": rdata})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# REPORTS
##########################################################################
def _summary_books_read_by_year(target_year=None):
    db = pymysql.connect(**conf)
    search_str = ("SELECT YEAR(b.ReadDate) as Year, SUM(a.Pages) as Pages, COUNT(a.Pages) as Books "
                  "FROM `book collection` as a JOIN `books read` as b "
                  "ON a.BookCollectionID = b.BookCollectionID "
                  "WHERE b.ReadDate is not NULL "
                  "AND b.ReadDate <> \"0000-00-00 00:00:00\" ")
    if target_year is not None:
        search_str += f" AND YEAR(b.ReadDate) = {target_year} "
    search_str += "GROUP BY Year ORDER BY Year ASC"
    header = ["year", "pages read", "books read"]
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


@app.route('/summary_books_read_by_year')
@app.route('/summary_books_read_by_year/<target_year>')
def summary_books_read_by_year(target_year=None):
    rdata, _, _ = _summary_books_read_by_year(target_year)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


def _books_read(target_year=None):
    db = pymysql.connect(**conf)
    search_str = ("SELECT a.*, b.ReadDate "
                  "FROM `book collection` as a JOIN `books read` as b "
                  "ON a.BookCollectionID = b.BookCollectionID "
                  "WHERE b.ReadDate is not NULL "
                  "AND b.ReadDate <> \"0000-00-00 00:00:00\" ")
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


@app.route('/books_read')
@app.route('/books_read/<target_year>')
def books_read(target_year=None):
    rdata, _, _ = _books_read(target_year)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/status_read/<book_id>')
def status_read(book_id=None):
    db = pymysql.connect(**conf)
    search_str = f"SELECT * FROM `books read` WHERE BookCollectionID = {book_id} ORDER BY ReadDate ASC;"
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
            _, s, _ = _tags_search(args.get(key))
            id_list = str(tuple([int(x[0]) for x in s]))
            app.logger.debug(id_list)
            where.append(f"a.BookCollectionID in {id_list}")
        else:
            where.append(f"a.{key} LIKE \"%{args.get(key)}%\"")
    where_str = " AND ".join(where)
    search_str = ("SELECT a.*, b.ReadDate "
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
        tag_list = [x[0] for x in s]
        s = list(s)
        rdata = json.dumps({"BookID": book_id, "tag_list": tag_list})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/update_tag_value/<current>/<updated>')
def update_tag_value(current, updated):
    db = pymysql.connect(**conf)
    with db:
        with db.cursor() as c:
            try:
                _updated = updated.lower().strip(" ")
                records = c.execute("UPDATE `tags labels` SET Label = '{}' WHERE Label = '{}'".format(
                    _updated, current))
                rdata = json.dumps({"data": {"tag_update": f"{current} >> {updated}", "updated_tags": records}})
            except pymysql.Error as e:
                app.logger.error(e)
                rdata = json.dumps({"error": str(e)})
        db.commit()
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


def _tags_search(match_str):
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


@app.route('/tags_search/<match_str>')
def tags_search(match_str):
    rdata, s, header = _tags_search(match_str)
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


# @app.route('/tag_maintenance')
# def tag_maintenance():
#     db = pymysql.connect(**conf)
#     rdata = {"tag_maintenance": {}}
#     with db:
#         with db.cursor() as c:
#             try:
#                 # lower case
#                 c.execute("UPDATE `tags` SET Tag = TRIM(LOWER(Tag))")
#                 db.commit()
#             except pymysql.Error as e:
#                 rdata = {"error": [str(e)]}
#                 app.logger.error(e)
#             try:
#                 # duplicates
#                 c.execute("SELECT COUNT(*) FROM tags")
#                 a = c.fetchall()
#                 rdata["tag_maintenance"]["tags_before"] = a[0][0]
#                 c.execute("truncate temp")
#                 c.execute("insert into temp (BookID, Tag) select distinct BookID, Tag from tags")
#                 c.execute("truncate tags")
#                 c.execute("insert into tags (BookID, Tag) select BookID, Tag from temp")
#                 c.execute("truncate temp")
#                 c.execute("delete from tags where Tag=''")
#                 db.commit()
#                 c.execute("SELECT COUNT(*) FROM tags")
#                 a = c.fetchall()
#                 rdata["tag_maintenance"]["tags_after"] = a[0][0]
#             except pymysql.Error as e:
#                 app.logger.error(e)
#                 if "error" in rdata:
#                     rdata["error"].append(e)
#                 else:
#                     rdata = {"error": [str(e)]}
#     rdata = json.dumps(rdata)
#     response_headers = resp_header(rdata)
#     return Response(response=rdata, status=200, headers=response_headers)


##########################################################################
# IMAGES
##########################################################################
@app.route("/image/year_progress_comparison.png")
@app.route("/image/year_progress_comparison.png/<window>")
def year_progress_comparison(window=15):
    window = int(window)
    img = BytesIO()
    _, s, h = _books_read()
    df1 = pd.DataFrame(s, columns=h)
    df1 = df1.set_index("ReadDate")
    df1.index = pd.to_datetime(df1.index)
    df1 = df1.groupby(df1.index.to_period('y')).cumsum().reset_index()
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
    _, s, h = _summary_books_read_by_year()
    df = pd.DataFrame(s, columns=h)
    df['pages read'] = df['pages read'].astype(float)
    df["rank"] = df["pages read"].rank(ascending=False)
    df.sort_values(by=["rank"], inplace=True)
    df.reset_index()
    now = df.loc[df.year == year]
    app.logger.debug(now)
    fig, axs = plt.subplots(3, 1, figsize=[10, 18])
    df.hist("pages read", bins=14, color="darkblue", ax=axs[0])
    axs[0].axvline(x=int(now["pages read"]), color="red")
    df.plot.bar(x="rank", y="pages read", width=.95, color="darkblue", ax=axs[1])
    axs[1].axvline(x=int(now["rank"]) - 1, color="red")
    df.sort_values("year").plot.bar(x="year", y="pages read", width=.95, color="darkblue", ax=axs[2])
    fig.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
