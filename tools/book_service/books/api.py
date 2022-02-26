__version__ = '0.1.0'

import pymysql
from flask import Flask, Response, request

from books_util import *

conf = get_configuration()
db = pymysql.connect(**conf)
# server configuration
app = Flask(__name__)


@app.route('/configuration')
def configuration():
    rdata = json.dumps({
        "configuration": conf,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/tag_counts')
@app.route('/tag_counts/<tag>')
def tag_counts(tag=None):
    search_str = "SELECT Tag, COUNT(Tag) as count FROM tags"
    if tag is not None:
        search_str += f" WHERE Tag LIKE \"{tag}%\""
    search_str += " GROUP BY Tag ORDER BY count DESC"
    header = ["tag", "count"]
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
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/tags/<id>')
def tags(id=None):
    search_str = f"SELECT Tag FROM tags WHERE BookID = {id} ORDER BY Tag"
    app.logger.debug(search_str)
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app.logger.error(e)
        rdata = json.dumps({"error": str(e)})
        rdata = {"error": str(e)}
    else:
        s = c.fetchall()
        tag_list = [x[0] for x in s]
        s = list(s)
        rdata = json.dumps({"BookID": f"{id}", "tag_list": f"{tag_list}"})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/books_read_by_year')
@app.route('/books_read_by_year/<target_year>')
def books_read_by_year(target_year=None):
    search_str = ("SELECT YEAR(LastRead) as Year, SUM(Pages) as Pages, COUNT(Pages) as Books\n"
                  "FROM `book collection`\n"
                  "WHERE LastRead is not NULL and LastRead <> \"0000-00-00 00:00:00\" and year(LastRead) <> \"1966\" ")
    if target_year is not None:
        search_str += f" AND YEAR(LastRead) = {target_year}\n"
    search_str += ("GROUP BY YEAR(LastRead)\n"
                   "ORDER BY LastRead ASC;")
    header = ["year", "pages read", "books read"]
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
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/books_read')
@app.route('/books_read/<target_year>')
def books_read(target_year=None):
    search_str = ("SELECT *\n"
                  "FROM `book collection`\n"
                  "WHERE LastRead is not NULL and LastRead <> \"0000-00-00 00:00:00\" ")
    if target_year is not None:
        search_str += f" and YEAR(LastRead) = {target_year}"
    search_str += " ORDER BY LastRead ASC;"
    header = table_header
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
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/books')
def books():
    # process any query parameters
    args = request.args
    where = []
    for key in args:
        if key == "BookCollectionID":
            where.append(f"{key} = \"{args.get(key)}\"")
        else:
            where.append(f"{key} LIKE \"%{args.get(key)}%\"")
    where_str = "AND".join(where)
    # run the query
    search_str = ("SELECT *\n"
                  "FROM `book collection`\n")
    if where_str != '':
        search_str += "\nWHERE " + where_str
    search_str += "\nORDER BY Author, Title ASC"
    header = table_header
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
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/update_tag_value/<current>/<updated>')
def update_tag_value(current, updated):
    c = db.cursor()
    try:
        records = c.execute("UPDATE `tags` SET Tag = '{}' WHERE Tag = '{}'".format(updated.lower().strip(), current))
        db.commit()
        rdata = json.dumps({"tag_update": f"{current} >> {updated}", "updated_tags": records})
    except pymysql.Error as e:
        app.logger.error(e)
        rdata = json.dumps({"error": str(e)})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/add_tag_by_id/<id>/<tag>')
def add_tag(self, id, tag):
    c = db.cursor()
    try:
        c.execute(f"insert into tags (BookID, Tag) values (%s, %s)", (id, tag))
        rdata = json.dumps({"BookID": f"{id}", "Tag": f"{tag}"})
    except pymysql.Error as e:
        app.logger.error(e)
        rdata = json.dumps({"error": str(e)})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
