#!/usr/bin/env python
#
# Written by Scott Hendrickson
#
# 2006/01/09
# 2019/12/15
#
# Tools for manipulating the book database 
###################################################

import sys
import json
import logging
import pymysql
import optparse

from spellchecker import SpellChecker

class bookDBTool:
    def __init__(self):
        self.db = pymysql.connect(host=DBHOST, port=3306, user=UN, passwd=PWD, db=DB)

    def show_tags(self):
        spell = SpellChecker()
        st = []
        c = self.db.cursor()
        try:
            c.execute(
                "SELECT Tag, COUNT(Tag) as count FROM tags GROUP BY Tag ORDER BY count DESC")
        except pymysql.Error as e:
            logging.error(e)
        else:
            s = c.fetchall()
            print("{} {} {}".format("#"*20, "tags", "#"*20))
            for i in s:
                w = spell.unknown(i[0].split(" "))
                suggest = []
                if len(w) > 0:
                    for j in w:
                        suggest.append(str(spell.candidates(j)))
                    suggest = ";".join(suggest)
                else:
                    suggest = ""
                print("  {}  ({})    {}".format(i[0], i[1], suggest))
                st.append(i[0])
        return st

    def show_locations(self):
        sl = []
        c = self.db.cursor()
        try:
            c.execute(
                "SELECT Location, COUNT(Location) as count FROM `book collection` GROUP BY Location ORDER BY count DESC")
        except pymysql.Error as e:
            logging.error(e)
        else:
            s = c.fetchall()
            print("{} {} {}".format("#" * 20, "locations", "#" * 20))
            for i in s:
                print("  {}  ({})".format(*i))
                sl.append(i[0])
        return sl

    def tag_from_category(self, tag, cat):
        cl = self.get_category_ID_list(cat)
        self.add_tag(cl, tag)

    def lower_case_tags(self):
        c = self.db.cursor()
        try:
            c.execute("UPDATE `tags` SET Tag = LOWER(Tag)")
            self.db.commit()
        except pymysql.Error as e:
            logging.error(e)

    def add_tag(self, cl, tag):
        c = self.db.cursor()
        for id in cl:
            print('Inserted: ', id)
        try:
            c.execute("insert into tags (BookID, Tag) values (%s, %s)", (id, tag))
        except pymysql.Error as e:
            logging.error(e)

    def get_category_ID_list(self, cat):
        c = self.db.cursor()
        cat_ID_list = []
        try:
            c.execute("select BookCollectionID from `book collection` where Category=%s", cat)
        except pymysql.Error as e:
            logging.error(e)
        else:
            s = c.fetchall()
            for i in s:
                cat_ID_list.append(i[0])
        return cat_ID_list

    def deduplicate_tags(self):
        c = self.db.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM tags")
            a = c.fetchall()
            print("Tags Before: {}".format(a[0][0]))
            c.execute("truncate temp")
            c.execute("insert into temp (BookID, Tag) select distinct BookID, Tag from tags")
            c.execute("truncate tags")
            c.execute("insert into tags (BookID, Tag) select BookID, Tag from temp")
            c.execute("truncate temp")
            c.execute("delete from tags where Tag=''")
            self.db.commit()
            c.execute("SELECT COUNT(*) FROM tags")
            a = c.fetchall()
            print("Tags After: {}".format(a[0][0]))
        except pymysql.Error as e:
            logging.error("Error %d: %s" % (e.args[0], e.args[1]))

    def close(self):
        self.db.close()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", default="./configuration.json", dest="config_filename",
        help="Configuration file for database access.")
    parser.add_option("-d", "--cleanup", action="store_true",dest="dup",
        help="Remove duplicate tag entries from Tag table. Set tags to lowercase.")
    parser.add_option("-f", dest="tagattr", nargs=2,
        help="Enter tag and field values, e.g. -f poetry Poetry. Each occurance of (field) in column Category will result in tagging the record with (tag).")
    parser.add_option("-s", "--show", action="store_true", dest="show",
        help="Show tags and fields.")
    (options, args) = parser.parse_args()

    with open(options.config_filename, "r") as config_file:
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

    bt = bookDBTool()
    if (options.tagattr):
        logging.info("Adding tag " + options.tagattr[0] + " to records in category " + options.tagattr[1])
        bt.tag_from_category(options.tagattr[0], options.tagattr[1])
    if (options.dup):
        logging.info("Updating all tags to lower case...")
        bt.lower_case_tags()
        logging.info("Removing duplicate and null tags...")
        bt.deduplicate_tags()
    if (options.show):
        logging.info("Tags:")
        bt.show_tags()
        logging.info("Locations:")
        bt.show_locations()
