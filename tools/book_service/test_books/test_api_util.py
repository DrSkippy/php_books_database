import datetime
import unittest

from books import api_util as au


class TestAppFunctions(unittest.TestCase):

    def test_const(self):
        self.assertEqual(len(au.locations_sort_order), 7)
        self.assertEqual(len(au.table_header), 13)
        self.assertTrue(len(au.API_KEY) > 0)

    def test_get_configuration(self):
        config1, config2 = au.get_configuration()
        self.assertGreaterEqual(len(config1['user']), 4)
        self.assertGreaterEqual(len(config1['passwd']), 4)
        self.assertEqual(config1["db"], "books")
        self.assertEqual(len(config2), 2)

    def test_sort_by_indexes(self):
        lst = [1, 2, 3, 4, 5]
        indexes = [4, 3, 2, 1, 0]
        sorted_lst = au.sort_by_indexes(lst, indexes)
        self.assertEqual(sorted_lst, [5, 4, 3, 2, 1])

    def test_serialize_rows(self):
        cursor = [(1, 'Title1', 'Author1', datetime.date(2022, 1, 1)),
                  (2, 'Title2', 'Author2', datetime.date(2022, 1, 2))]
        header = ['ID', 'Title', 'Author', 'Date']
        expected_result = '{"header": ["ID", "Title", "Author", "Date"], "data": [[1, "Title1", "Author1", "2022-01-01"], [2, "Title2", "Author2", "2022-01-02"]]}'
        result = au.serialize_rows(cursor, header)
        self.assertEqual(result, expected_result)

    def test_resp_header(self):
        rdata = '{"header": ["ID", "Title", "Author", "Date"], "data": [[1, "Title1", "Author1", "2022-01-01"], [2, "Title2", "Author2", "2022-01-02"]]}'
        response_header = au.resp_header(rdata)
        print(response_header)
        expected_header = [
            ('Content-type', 'application/json; charset=utf-8'),
            ('Content-Length', str(len(rdata)))
        ]
        self.assertEqual(response_header, expected_header)

    def test_summary_books_read_by_year(self):
        res = au.summary_books_read_by_year_utility(target_year=1966)
        self.assertEqual(len(res), 3)
        self.assertEqual(str(res),
                         """('{"header": ["year", "pages read", "books read"], "data": [[1966, 2527.0, 13]]}', ((1966, Decimal('2527'), 13),), ['year', 'pages read', 'books read'])""")

    def test_books_read(self):
        res = au.books_read_utility(target_year=1966)
        self.assertEqual(len(res), 3)
        # print(res)
        print(str(res[1])[:65])
        self.assertEqual(str(res[1])[:65],
                         """((155, 'Letters To Children', 'Lewis, C S', datetime.datetime(198""")

    def test_tags_search(self):
        res = au.tags_search_utility("zander")
        self.assertEqual(len(res), 3)
        print(str(res[2]))
        self.assertEqual(str(res[2]),
                         """['BookCollectionID', 'TagID', 'Tag']""")

    def test_depending_on_daily_page_record_from_db(self):
        d, _ = au.daily_page_record_from_db(1)
        self.assertEqual(len(d), 4)
        self.assertEqual(str(d[3]), '[datetime.datetime(2022, 2, 9, 0, 0), 279, 8]')

    def test_depending_on_reading_book_data_from_db(self):
        res = au.reading_book_data_from_db(1)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[1], 1)
        self.assertEqual(res[0][0], (datetime.datetime(2022, 2, 1, 0, 0), 788))

        d, _ = au.daily_page_record_from_db(1)
        print(res[0][0])
        res1 = au.estimate_completion_dates(d, 1000)
        self.assertEqual(len(res), 2)
        self.assertEqual(res1[0], datetime.datetime(2022, 5, 16, 0, 0))
        self.assertEqual(res1[1], datetime.datetime(2022, 4, 25, 0, 0))
        self.assertEqual(res1[2], datetime.datetime(2022, 11, 6, 0, 0))

    def test_calculate_estimates(self):
        res = au.calculate_estimates(1)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], "2022-04-18")
        self.assertEqual(res[1], "2022-04-03")
        self.assertEqual(res[2], "2022-08-18")

    def test_get_book_ids_(self):
        book_ids = au.get_book_ids(2, 20)
        print(book_ids)
        self.assertEqual(book_ids, [1869, 1870, 1871, 1872, 1873, 1874, 1875, 1876,
                                    1877, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertEqual(len(book_ids), 20)
        book_ids = au.get_book_ids(1875, 20)  # last as of 2025-11-26
        print(book_ids)
        self.assertEqual(book_ids, [1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873,
                                    1874, 1875, 1876, 1877, 2, 3, 4, 5, 6, 7, 8, 9])

        self.assertEqual(len(book_ids), 20)
        book_ids = au.get_book_ids(477, 30)
        print(book_ids)
        self.assertEqual(len(book_ids), 30)

    def test_complete_book_record(self):
        rec = au.complete_book_record(1873)
        print(rec)
        self.assertEqual(len(rec), 3)
        self.assertEqual(rec["book"]["data"][0][0], 1873)
        self.assertEqual(rec["book"]["data"][0][7], 548)
        self.assertEqual(len(rec["reads"]["data"]), 1)
        self.assertEqual(len(rec["tags"]["data"][0]), 8)


if __name__ == '__main__':
    unittest.main()
