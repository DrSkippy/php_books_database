import json

import requests

ENDPOINT = "http://localhost"
EXAMPLES_PATH = "./example_json_payloads"
API_KEY = 'sdf876a234hqkajsdv9876x87ehruia76df'


def test_configuration():
    ep = ENDPOINT + "/configuration"
    print(f"QUERY={ep}")
    r = requests.get(ep, headers={'x-api-key': 'sdf876a234hqkajsdv9876x87ehruia76df'})
    print(r.json())
    assert(r.status_code == 200)

def test_configuration():
    ep = ENDPOINT + "/configuration"
    print(f"QUERY={ep}")
    r = requests.get(ep)
    print(r.status_code)
    assert(r.status_code == 401)

def test_locations():
    ep = ENDPOINT + "/valid_locations"
    print(f"QUERY={ep}")
    r = requests.get(ep, headers={'x-api-key': 'sdf876a234hqkajsdv9876x87ehruia76df'})
    print(r.json())
    assert(r.status_code == 200)


def test_add_books():
    ep = ENDPOINT + "/add_books"
    print(f"QUERY={ep}")
    with open(f"{EXAMPLES_PATH}/test_add_books.json", "r") as infile:
        data = json.load(infile)
    r = requests.post(ep, json=data, headers={'x-api-key': f'{API_KEY}'})
    print(r.json())
    assert(r.status_code == 200)
    res = [x["BookCollectionID"] for x in r.json()["add_books"]]
    return res


def test_add_read_dates(book_id_list):
    ep = ENDPOINT + "/add_read_dates"
    print(f"QUERY={ep}")
    with open(f"{EXAMPLES_PATH}/test_update_read_dates.json", "r") as infile:
        data = json.load(infile)
    for x, r in zip(data, book_id_list):
        x["BookCollectionID"] = r
    res = requests.post(ep, json=data, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)


def test_update_book_note_status(id):
    ep = ENDPOINT + "/update_book_note_status"
    print(f"QUERY={ep}")
    with open(f"{EXAMPLES_PATH}/test_update_book_note_status.json", "r") as infile:
        data = json.load(infile)
    data["BookCollectionID"] = int(id)
    res = requests.post(ep, json=data, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)


def test_summary_books_read_by_year(year=2015):
    ep = ENDPOINT + f"/summary_books_read_by_year/{year}"
    print(f"QUERY={ep}")
    res = requests.get(ep, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)
    ep1 = ENDPOINT + "/summary_books_read_by_year"
    print(f"QUERY={ep1}")
    res1 = requests.get(ep1, headers={'x-api-key': f'{API_KEY}'})
    print(res1.json())
    assert(res1.status_code == 200)


def test_books_read(year=2015):
    ep = ENDPOINT + f"/books_read/{year}"
    print(f"QUERY={ep}")
    res = requests.get(ep, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)
    ep1 = ENDPOINT + "/books_read"
    print(f"QUERY={ep1}")
    res1 = requests.get(ep1, headers={'x-api-key': f'{API_KEY}'})
    print(res1.json())
    assert(res1.status_code == 200)


def test_books_search():
    ep = ENDPOINT + "/books_search"
    ep1 = ep + "?Author=lewis"
    print(f"QUERY={ep1}")
    res1 = requests.get(ep1, headers={'x-api-key': f'{API_KEY}'})
    print(res1.json())
    assert(res1.status_code == 200)
    ep2 = ep + "?PublisherName=dover"
    res2 = requests.get(ep2, headers={'x-api-key': f'{API_KEY}'})
    print(res2.json())
    assert(res2.status_code == 200)


def test_add_tags(book_ids):
    ep = ENDPOINT + "/add_tag"
    print(f"QUERY={ep}")
    for book_id in book_ids:
        res = requests.put(ep + f"/{book_id}/deleteme", headers={'x-api-key': f'{API_KEY}'})
        print(res.json())
        assert(res.status_code == 200)


def test_tag_counts():
    ep = ENDPOINT + "/tag_counts/deleteme"
    print(f"QUERY={ep}")
    res = requests.get(ep, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)


def test_tags(id):
    ep = ENDPOINT + f"/tags/{id}"
    print(f"QUERY={ep}")
    res = requests.get(ep, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)


def test_update_tag_value():
    ep = ENDPOINT + "/update_tag_value/deleteme/delete_me"
    print(f"QUERY={ep}")
    res = requests.get(ep, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)


def test_tags_search():
    ep = ENDPOINT + "/tags_search/apple"
    print(f"QUERY={ep}")
    res = requests.get(ep, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)
    ep2 = ENDPOINT + "/tags_search/dog"
    res2 = requests.get(ep2, headers={'x-api-key': f'{API_KEY}'})
    print(res2.json())
    assert(res2.status_code == 200)


def test_tag_maintenance():
    ep = ENDPOINT + "/tag_maintenance"
    print(f"QUERY={ep}")
    res = requests.get(ep, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)


def test_status_read(id):
    ep = ENDPOINT + f"/status_read/{id}"
    print(f"QUERY={ep}")
    res = requests.get(ep, headers={'x-api-key': f'{API_KEY}'})
    print(res.json())
    assert(res.status_code == 200)


if __name__ == "__main__":
    test_configuration()
    test_locations()
    r = test_add_books()
    test_add_read_dates(r)
    test_update_book_note_status(r[0])
    test_summary_books_read_by_year()
    test_books_read()
    test_books_search()
    test_add_tags(r)
    test_tag_counts()
    test_tags(2)
    test_update_tag_value()
    test_tags_search()
    test_tag_maintenance()
    test_status_read(1696)

    print("""For DB Cleanup:
    
    USE books;
    DELETE FROM `tag labels` where label='delete_me';
    DELETE FROM `book collection` WHERE PublisherName='Printerman';
    DELETE FROM `books read` WHERE ReadDate='1945-10-19';
    """)
