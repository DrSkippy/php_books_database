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
import optparse

from bookdbtool.tools import bookDBTool

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", default="./configuration.json", dest="config_filename",
        help="Configuration file for database access.")
    parser.add_option("-d", "--cleanup", action="store_true",dest="dup",
        help="Remove duplicate tag entries from Tag table. Set tags to lowercase.")
    parser.add_option("-f", dest="tagattr", nargs=2,
        help="Enter tag and field values, e.g. -f poetry Poetry. Each occurrence of" + \
             " (field) in column Category will result in tagging the record with (tag).")
    parser.add_option("-s", "--show", action="store_true", dest="show",
        help="Show tags and fields.", default=False)
    parser.add_option("-t", "--show_only_spell", action="store_true", dest="only_spell", default=False,
        help="Show tags and fields.")
    parser.add_option("--csv", action="store_true", dest="dumpcsv", default=False,
        help="CSV dump from pandas")
    parser.add_option("-u", dest="current_update", nargs=2,
        help="Enter current tag value and updated tag value, e.g. -u poetyr poetry.")
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

    bt = bookDBTool(DBHOST, UN, PWD, DB)
    if (options.tagattr):
        logging.info("Adding tag " + options.tagattr[0] + " to records in category " + options.tagattr[1])
        bt.tag_from_category(options.tagattr[0], options.tagattr[1])
    if (options.current_update):
        logging.info("Updating tag " + options.current_update[0] + " to " + options.current_update[1])
        bt.update_tag_value(options.current_update[0], options.current_update[1])
    if (options.dup):
        logging.info("Updating all tags to lower case...")
        bt.lower_case_tags()
        logging.info("Removing duplicate and null tags...")
        bt.deduplicate_tags()
    if (options.show or options.only_spell):
        logging.info("Tags:")
        bt.show_tags(only_spell=options.only_spell)
        logging.info("Locations:")
        bt.show_locations()
    if (options.dumpcsv):
        df = bt.get_dataframe()
        print(df.to_csv())
    bt.close()
