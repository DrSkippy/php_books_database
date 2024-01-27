from bookdbtool import estimate_tools as et

def test_reading_data_from_db():
    BookID = 1715
    data = et._daily_page_record_from_db(BookID)
    print(data)

def test_book_reading_data_from_db():
    BookID = 1715
    data = et._reading_book_data_from_db(BookID)
    print(data)

def test_estimate_dates():
    BookID = 1715
    reading_data, _ = et._reading_data_from_db(BookID)
    book_data, _ = et._reading_book_data_from_db(BookID)
    print(book_data)
    a = et._estimate_dates(reading_data, book_data[0][0], book_data[0][1])
    print(a)

if __name__ == "__main__":
    test_reading_data_from_db()
    test_book_reading_data_from_db()
    test_estimate_dates()
