__version__ = '0.4.0'

import pymysql
from flask import Flask, Response, request

from books_util import *

conf = get_configuration()
# server configuration
app = Flask(__name__)


@app.route('/configuration')
def configuration():
    db = pymysql.connect(**conf)
    rdata = json.dumps({
        "version": __version__,
        "configuration": conf,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


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
    db = pymysql.connect(**conf)
    records = request.get_json()
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


@app.route('/update_read_dates', methods=['POST'])
def update_read_dates():
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
    rdata = []
    with db:
        with db.cursor() as c:
            try:
                c.execute(search_str.format(**record))
                print(search_str.format(**record))
                rdata.append(record)
            except pymysql.Error as e:
                app.logger.error(e)
                rdata.append({"error": str(e)})
        db.commit()
    rdata = json.dumps({"update_book": rdata})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/summary_books_read_by_year')
@app.route('/summary_books_read_by_year/<target_year>')
def summary_books_read_by_year(target_year=None):
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

@app.route('/books_read')
@app.route('/books_read/<target_year>')
def books_read(target_year=None):
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
        else:
            where.append(f"a.{key} LIKE \"%{args.get(key)}%\"")
    where_str = "AND".join(where)
    search_str = ("SELECT a.*, b.ReadDate "
                  "FROM `book collection` as a LEFT JOIN `books read` as b "
                  "ON a.BookCollectionID = b.BookCollectionID ")
    if where_str != '':
        search_str += "WHERE " + where_str
    search_str += " ORDER BY a.Author, a.Title ASC"
    header = table_header + ["ReadDate"]
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
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/add_tag_by_id/<id>/<tag>', methods=["put"])
def add_tag(id, tag):
    db = pymysql.connect(**conf)
    with db:
        with db.cursor() as c:
            try:
                c.execute("INSERT IGNORE INTO tags (BookID, Tag) VALUES (%s, %s)", (id, tag))
                rdata = json.dumps({"BookID": f"{id}", "Tag": f"{tag}"})
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
    search_str = "SELECT Tag, COUNT(Tag) as Count FROM tags"
    if tag is not None:
        search_str += f" WHERE Tag LIKE \"{tag}%\""
    search_str += " GROUP BY Tag ORDER BY count DESC"
    header = ["Tag", "Count"]
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


@app.route('/tags/<id>')
def tags(id=None):
    db = pymysql.connect(**conf)
    search_str = f"SELECT Tag FROM tags WHERE BookID = {id} ORDER BY Tag"
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
        rdata = json.dumps({"BookID": id, "tag_list": tag_list})
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/update_tag_value/<current>/<updated>')
def update_tag_value(current, updated):
    db = pymysql.connect(**conf)
    with db:
        with db.cursor() as c:
            try:
                _updated = updated.lower().strip(" ")
                records = c.execute("UPDATE `tags` SET Tag = '{}' WHERE Tag = '{}'".format(
                    _updated, current))
                rdata = json.dumps({"tag_update": f"{current} >> {updated}", "updated_tags": records})
            except pymysql.Error as e:
                app.logger.error(e)
                rdata = json.dumps({"error": str(e)})
        db.commit()
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
