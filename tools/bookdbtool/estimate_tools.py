import csv
import datetime
import os

import numpy as np

FMT = "%Y-%m-%d"
ESTIMATES_PATH = "./book_estimates"
file_list = []


def new(title):
    fn = title.strip().lower().replace(" ", "_").replace(":", "")
    filename = f"{ESTIMATES_PATH}/{fn}.txt"
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


def make(index=0, filename=None):
    global records_file_list
    if filename is None:
        filename = records_file_list[index]
    filename = ESTIMATES_PATH + "/" + filename
    data, header = _reading_data(filename)
    est_date, est_date_min, est_date_max = _estimate_dates(data, header)
    print("*" * 80)
    print(f"Book: {header[0]}")
    print("Estimated Complete: {}  Earliest: {}  Latest: {}".format(est_date.strftime(FMT),
                                                                    est_date_min.strftime(FMT),
                                                                    est_date_max.strftime(FMT)))
    print("*" * 80)

def add_date_pages(pages, index, date=None, filename=None):
    if date is None:
        date = datetime.datetime.now().strftime(FMT)
    if filename is None:
        filename = records_file_list[index]
    filename = ESTIMATES_PATH + "/" + filename
    with open(filename, "a") as of:
        of.write("{}, {}\n".format(date, pages))
    make(filename=filename)


def list(path=ESTIMATES_PATH):
    global records_file_list
    records_file_list = os.listdir(path)
    print("Existing files: ")
    for i, file in enumerate(records_file_list):
        print(f"    {i} - {file}")

def _day_number(data):
    # title, total pages to read
    # date, page
    # ...
    # in date order, so pages are increasing monotonically
    start_date = data[0][2]
    for row in data:
        row.append((row[2] - start_date).days)
    return data, start_date


def _estimate_range(x, y, p):
    res = [0, 10000]
    for i in range(len(x) - 1):
        m = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
        est = int(m * (p - np.max(x)) + np.max(y))
        if est > res[0]:
            res[0] = est
        if est < res[1]:
            res[1] = est
    return res


def _line_fit_and_estimate(data, total_pages):
    d = np.array(data)
    x = np.array(d[:, 1], dtype=np.float64)
    y = np.array(d[:, 3], dtype=np.float64)
    m, b = np.polyfit(x, y, 1)
    est = m * float(total_pages) + b
    est_range = _estimate_range(x, y, total_pages)
    return int(est), est_range


def _reading_data(filename):
    header = None
    data = []
    with open(filename, "r") as book_file:
        rdr = csv.reader(book_file)
        for row in rdr:
            if header is None:
                header = row
            else:
                if row[0].startswith("#") or row[1] is None or row[1] == "":
                    continue
                else:
                    row.append(datetime.datetime.strptime(row[0], FMT))
                    data.append(row)
    return data, header


def _estimate_dates(data, header):
    data, start_date = _day_number(data)
    est, range = _line_fit_and_estimate(data, float(header[1]))
    est_date = start_date + datetime.timedelta(days=est)
    est_date_max = start_date + datetime.timedelta(days=range[0])
    est_date_min = start_date + datetime.timedelta(days=range[1])
    return est_date, est_date_min, est_date_max
