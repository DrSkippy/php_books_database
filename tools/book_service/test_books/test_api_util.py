import datetime
import unittest
from unittest.mock import patch, MagicMock

from books.api_util import *


class TestAppFunctions(unittest.TestCase):


    def test_get_configuration(self):
        config1, config2 = get_configuration()
        self.assertGreaterEqual(len(config1['user']), 4)
        self.assertGreaterEqual(len(config1['passwd']), 4)
        self.assertEquals(config1["db"], "books")
        self.assertEquals(len(config2), 2)

    def test_sort_by_indexes(self):
        lst = [1, 2, 3, 4, 5]
        indexes = [4, 3, 2, 1, 0]
        sorted_lst = sort_by_indexes(lst, indexes)
        self.assertEqual(sorted_lst, [5, 4, 3, 2, 1])

    def test_serialize_rows(self):
        cursor = [(1, 'Title1', 'Author1', datetime.date(2022, 1, 1)),
                  (2, 'Title2', 'Author2', datetime.date(2022, 1, 2))]
        header = ['ID', 'Title', 'Author', 'Date']
        expected_result = '{"header": ["ID", "Title", "Author", "Date"], "data": [[1, "Title1", "Author1", "2022-01-01"], [2, "Title2", "Author2", "2022-01-02"]]}'
        result = serialize_rows(cursor, header)
        self.assertEqual(result, expected_result)

    def test_resp_header(self):
        rdata = '{"header": ["ID", "Title", "Author", "Date"], "data": [[1, "Title1", "Author1", "2022-01-01"], [2, "Title2", "Author2", "2022-01-02"]]}'
        response_header = resp_header(rdata)
        expected_header = [
            ('Access-Control-Allow-Origin', '*'),
            ('Content-type', 'application/json'),
            ('Content-Length', str(len(rdata)))
        ]
        self.assertEqual(response_header, expected_header)

    @patch('books.api_util.pymysql.connect')
    def test_daily_page_record_from_db(self, mock_connect):
        # Mocking the database connection
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(datetime.date(2022, 1, 1), 100), (datetime.date(2022, 1, 2), 200)]
        mock_connect.return_value.cursor.return_value = mock_cursor
        #
        # Testing the function
        data, record_id = daily_page_record_from_db(1)
        expected_data = [
            [datetime.date(2022, 1, 1), 100, 0],
            [datetime.date(2022, 1, 2), 200, 1]
        ]
        self.assertEqual(data, expected_data)
        self.assertEqual(record_id, 1)
#
#     @patch('books.api_util.pymysql.connect')
#     def test_reading_book_data_from_db(self, mock_connect):
#         # Mocking the database connection
#         mock_cursor = MagicMock()
#         mock_cursor.fetchall.return_value = [(datetime.date(2022, 1, 1), 300)]
#         mock_connect.return_value.cursor.return_value = mock_cursor
#
#         # Testing the function
#         data, record_id = reading_book_data_from_db(1)
#         expected_data = [
#             [datetime.date(2022, 1, 1), 300]
#         ]
#         self.assertEqual(data, expected_data)
#         self.assertEqual(record_id, 1)
#
#     @patch('datetime')
#     @patch('books.api_util.update_reading_book_data')
#     def test_calculate_estimates(self, mock_update, mock_datetime):
#         mock_datetime.timedelta.return_value = datetime.timedelta(days=3)
#         reading_data = [
#             [datetime.date(2022, 1, 1), 100, 0],
#             [datetime.date(2022, 1, 2), 200, 1]
#         ]
#         book_data = [
#             [datetime.date(2022, 1, 1), 300]
#         ]
#         mock_daily_page_record_from_db = MagicMock(return_value=(reading_data, 1))
#         mock_reading_book_data_from_db = MagicMock(return_value=(book_data, 1))
#         with patch('daily_page_record_from_db', mock_daily_page_record_from_db), \
#                 patch('reading_book_data_from_db', mock_reading_book_data_from_db):
#             estimates = calculate_estimates(1)
#             expected_estimates = ['2022-01-04', '2022-01-02', '2022-01-03']
#             self.assertEqual(estimates, expected_estimates)
#             mock_update.assert_called_once_with(1, [datetime.date(2022, 1, 4), datetime.date(2022, 1, 2),
#                                                     datetime.date(2022, 1, 3)])


if __name__ == '__main__':
    unittest.main()
