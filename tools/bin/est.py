#!/usr/bin/env python
#
# Written by Scott Hendrickson
#
# Tools for estimating book reading completion date
# Usage:
# poetry run python bin/est.py ./book_estimates/command-control.txt
###################################################
import sys

from bookdbtool.estimate_tools import *

if len(sys.argv) < 2:
    # setup and estimate
    title = input("Enter book title: ")
    fn = title.strip().lower().replace(" ", "_")
    filename = f"./book_estimates/{fn}.txt"
    start_date_str = input("Enter start date (YYYY-MM-DD): ")
    start_date = datetime.datetime.strptime(start_date_str, FMT)
    pages = int(input("Number of pages: "))
    print(f"Book Title={title}")
    print(f"File Name={filename}")
    print(f"Start Date={start_date}")
    with open(filename, "w") as of:
        of.write(f"\"{title}\", {pages}\n")
        for i in range(30):
            dt = start_date + datetime.timedelta(days=i)
            of.write("{},\n".format(dt.strftime(FMT)))
else:
    # estimate
    filename = sys.argv[1]
    data, header = reading_data(filename)
    est_date, est_date_min, est_date_max = estimate_dates(data, header)
    print("*" * 80)
    print(f"              Book: {header[0]}")
    print("Estimated Complete: {}  Earliest: {}  Latest: {}".format(est_date.strftime(FMT), est_date_min.strftime(FMT),
                                                                    est_date_max.strftime(FMT)))
    print("*" * 80)
