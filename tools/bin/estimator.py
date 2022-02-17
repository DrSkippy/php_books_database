#!/usr/bin/env python
#
# Written by Scott Hendrickson
#
# Tools for estimating book reading completion date
# Usage:
# poetry run python bin/estimator.py ./book_estimates/command-control.txt
###################################################
import csv
import datetime
import sys

import numpy as np

FMT = "%Y-%m-%d"


def day_number(date):
    # title, total pages to read
    # date, page
    # ...
    # in date order, so pages are increasing monotonically
    start_date = data[0][2]
    for row in data:
        row.append((row[2] - start_date).days)
    return data, start_date


def estimate_range(x, y, p):
    res = [0, 10000]
    for i in range(len(x) - 1):
        m = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
        est = int(m * (p - np.max(x)) + np.max(y))
        if est > res[0]:
            res[0] = est
        if est < res[1]:
            res[1] = est
    return res


def line_fit_and_estimate(data, total_pages):
    d = np.array(data)
    x = np.array(d[:, 1], dtype=np.float)
    y = np.array(d[:, 3], dtype=np.float)
    m, b = np.polyfit(x, y, 1)
    est = m * float(total_pages) + b
    est_range = estimate_range(x, y, total_pages)
    return int(est), est_range


###################################################
filename = sys.argv[1]
header = None
data = []
with open(filename, "r") as book_file:
    rdr = csv.reader(book_file)
    for row in rdr:
        if header is None:
            header = row
        else:
            row.append(datetime.datetime.strptime(row[0], FMT))
            data.append(row)

data, start_date = day_number(data)
est, range = line_fit_and_estimate(data, float(header[1]))
est_date = start_date + datetime.timedelta(days=est)
est_date_max = start_date + datetime.timedelta(days=range[0])
est_date_min = start_date + datetime.timedelta(days=range[1])

print(f"Book: {header[0]}")
print("Estimated complete: {}  Earliest: {} Latest: {}".format(est_date.strftime(FMT), est_date_min.strftime(FMT),
                                                               est_date_max.strftime(FMT)))
