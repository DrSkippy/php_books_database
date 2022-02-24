__version__ = '0.1.0'

import datetime
import json
import logging
from decimal import Decimal

import pymysql
# import requests
# import random
from flask import Flask, Response

config_filename = "./config/configuration.json"
with open(config_filename, "r") as config_file:
    logging.debug(f"opening configuration file {config_filename}")
    c = json.load(config_file)
    logging.debug("{}".format(c))
    try:
        UN = c["username"].strip()
        PWD = c["password"].strip()
        DB = c["database"].strip()
        DBHOST = c["host"].strip()
    except KeyError as e:
        logging.error(e)
        sys.exit()

db = pymysql.connect(host=DBHOST, port=3306, user=UN, passwd=PWD, db=DB)

# server configuration
app = Flask(__name__)


def serialize_rows(cursor):
    res = []
    for row in cursor:
        _row = []
        for d in row:
            if isinstance(d, Decimal):
                _row.append(float(d))
            elif isinstance(d, datetime.datetime):
                _row.append(d.strftime("%Y-%m-%d"))
            else:
                _row.append(d)
        app.logger.debug(f"row={_row}")
        res.append(_row)
    return json.dumps(res)


#################################################

@app.route('/')
def main():
    rdata = json.dumps({"key": "Hello World"})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/tags')
def show_tags():
    rdata = []
    c = db.cursor()
    try:
        c.execute("SELECT Tag, COUNT(Tag) as count FROM tags GROUP BY Tag ORDER BY count DESC")
    except pymysql.Error as e:
        app.logger.error(e)
    else:
        s = c.fetchall()
        rdata = serialize_rows(s)
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/books_year/<target_year>')
@app.route('/books_year')
def books_year(target_year=None):
    rdata = []
    search_str = """ SELECT YEAR(LastRead), SUM(Pages) as Pages, COUNT(Pages) as Books
                FROM `book collection`
                WHERE LastRead is not NULL and LastRead <> "0000-00-00 00:00:00" and year(LastRead) <> "1966" """
    if target_year is not None:
        search_str += f" and YEAR(LastRead) = {target_year}"
    search_str += """
                GROUP BY YEAR(LastRead)
                ORDER BY LastRead ASC;"""
    app.logger.debug(search_str)
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app.logger.error(e)
    else:
        s = c.fetchall()
        rdata = serialize_rows(s)
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/books_read/<target_year>')
@app.route('/books_read')
def books_read(target_year=None):
    rdata = []
    search_str = """ SELECT *
                FROM `book collection`
                WHERE LastRead is not NULL and LastRead <> "0000-00-00 00:00:00" """
    if target_year is not None:
        search_str += f" and YEAR(LastRead) = {target_year}"
    search_str += """
                ORDER BY LastRead ASC;"""
    app.logger.debug(search_str)
    c = db.cursor()
    try:
        c.execute(search_str)
    except pymysql.Error as e:
        app.logger.error(e)
    else:
        s = c.fetchall()
        rdata = serialize_rows(s)
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
