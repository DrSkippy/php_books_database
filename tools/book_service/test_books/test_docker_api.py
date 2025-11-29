import json
import unittest

import requests
from books import api_util as au

ENDPOINT = "http://localhost:9999"
EXAMPLES_PATH = "./example_json_payloads"


class TestAppFunctions(unittest.TestCase):

    def setUp(self):
        ep = ENDPOINT + "/add_books"
        print(f"QUERY={ep}")
        with open(f"{EXAMPLES_PATH}/test_add_books.json", "r") as infile:
            data = json.load(infile)
        r = requests.post(ep, json=data, headers={'x-api-key': f'{au.API_KEY}'})
        print(r.json())
        self.assertTrue(r.status_code == 200)
        self.book_id_list = [x["BookCollectionID"] for x in r.json()["add_books"]]

    def test_configuration(self):
        ep = ENDPOINT + "/configuration"
        print(f"QUERY={ep}")
        r = requests.get(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(r.json())
        self.assertTrue(r.status_code == 200)

    def test_configuration1(self):
        ep = ENDPOINT + "/configuration"
        print(f"QUERY={ep}")
        r = requests.get(ep)
        print(r.status_code)
        self.assertTrue(r.status_code == 401)

    def test_locations(self):
        ep = ENDPOINT + "/valid_locations"
        print(f"QUERY={ep}")
        r = requests.get(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(r.json())
        self.assertTrue(r.status_code == 200)

    def test_books_search(self):
        ep = ENDPOINT + "/books_search"
        ep1 = ep + "?Author=lewis"
        print(f"QUERY={ep1}")
        res1 = requests.get(ep1, headers={'x-api-key': f'{au.API_KEY}'})
        print(res1.json())
        self.assertTrue(res1.status_code == 200)
        ep2 = ep + "?PublisherName=dover"
        res2 = requests.get(ep2, headers={'x-api-key': f'{au.API_KEY}'})
        print(res2.json())
        self.assertTrue(res2.status_code == 200)

    def test_tag_counts(self):
        ep = ENDPOINT + "/tag_counts/deleteme"
        print(f"QUERY={ep}")
        res = requests.get(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)

    def test_update_tag_value(self):
        ep = ENDPOINT + "/update_tag_value/deleteme/delete_me"
        print(f"QUERY={ep}")
        res = requests.put(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)

    def test_tags_search(self):
        ep = ENDPOINT + "/tags_search/apple"
        print(f"QUERY={ep}")
        res = requests.get(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)
        ep2 = ENDPOINT + "/tags_search/dog"
        res2 = requests.get(ep2, headers={'x-api-key': f'{au.API_KEY}'})
        print(res2.json())
        self.assertTrue(res2.status_code == 200)

    def test_tag_maintenance(self):
        ep = ENDPOINT + "/tag_maintenance"
        print(f"QUERY={ep}")
        res = requests.get(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)

    def test_add_read_dates(self):
        book_id_list = self.book_id_list
        ep = ENDPOINT + "/add_read_dates"
        print(f"QUERY={ep}")
        with open(f"{EXAMPLES_PATH}/test_update_read_dates.json", "r") as infile:
            data = json.load(infile)
        for x, r in zip(data, book_id_list):
            x["BookCollectionID"] = r
        res = requests.post(ep, json=data, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)

    def test_update_book_note_status(self):
        id = self.book_id_list[0]
        ep = ENDPOINT + "/update_book_note_status"
        print(f"QUERY={ep}")
        with open(f"{EXAMPLES_PATH}/test_update_book_note_status.json", "r") as infile:
            data = json.load(infile)
        data["BookCollectionID"] = int(id)
        res = requests.post(ep, json=data, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)

    def test_summary_books_read_by_year(self):
        year=2015
        ep = ENDPOINT + f"/summary_books_read_by_year/{year}"
        print(f"QUERY={ep}")
        res = requests.get(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)
        ep1 = ENDPOINT + "/summary_books_read_by_year"
        print(f"QUERY={ep1}")
        res1 = requests.get(ep1, headers={'x-api-key': f'{au.API_KEY}'})
        print(res1.json())
        self.assertTrue(res1.status_code == 200)

    def test_books_read(self):
        year = 2015
        ep = ENDPOINT + f"/books_read/{year}"
        print(f"QUERY={ep}")
        res = requests.get(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)
        ep1 = ENDPOINT + "/books_read"
        print(f"QUERY={ep1}")
        res1 = requests.get(ep1, headers={'x-api-key': f'{au.API_KEY}'})
        print(res1.json())
        self.assertTrue(res1.status_code == 200)

    def test_add_tags(self):
        book_ids = self.book_id_list
        ep = ENDPOINT + "/add_tag"
        print(f"QUERY={ep}")
        for book_id in book_ids:
            res = requests.put(ep + f"/{book_id}/deleteme", headers={'x-api-key': f'{au.API_KEY}'})
            print(res.json())
            self.assertTrue(res.status_code == 200)

    def test_tags(self):
        id = 2
        ep = ENDPOINT + f"/tags/{id}"
        print(f"QUERY={ep}")
        res = requests.get(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)

    def test_status_read(self):
        id = 1696
        ep = ENDPOINT + f"/status_read/{id}"
        print(f"QUERY={ep}")
        res = requests.get(ep, headers={'x-api-key': f'{au.API_KEY}'})
        print(res.json())
        self.assertTrue(res.status_code == 200)

    @classmethod
    def tearDownClass(cls):
        print("""For DB Cleanup:
        
        USE books;
        DELETE FROM `tag labels` where label="delete_me";
        DELETE FROM `book collection` WHERE PublisherName="Printerman";
        DELETE FROM `books read` WHERE ReadDate="1945-10-19";
        """)

if __name__ == "__main__":
    unittest.main()