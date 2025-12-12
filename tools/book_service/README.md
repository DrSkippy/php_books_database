# Test Book Service

## Tests

```
cat config/configuration.json | jq . 
docker images 
docker build -f ./books/Dockerfile . -t books-test
docker run -d -p 9999:8083 --name books-test-container books-test
docker ps
poetry run python test_books/generate_curl_commands.py > curl_test_script.bash
bash curl_test_script.bash
# note DELETEs...
poetry run pytest --cov-report term-missing --cov=books test_books/test_api_util.py
poetry run pytest -s test_books/test_docker_api.py 
# note DELETES...
docker rm -f books-test-container
```

### Test Cleanup:

- remove test records from database in DBeaver or other MySQL client
- remove generated images in test_books/...

```
rm *.png
rm curl_test_script.bash 
```


### Basic API Endpoints harvested from api.py in test script:


```
# Sample data for endpoints:
#   <target_year>: 2022
#   <book_id>: 1873
#   <tag>: fiction
#   <year>: 2020
#   <match_str>: Lewis
#   <current>: recovery
#   <updated>: recovery
#   <window>: 20
#   <record_id>: 50
#   <last_readable_page>: 15000
#   <start_date>: 1945-10-19


# Getting all of the GET endpoints from book_service/books/api.py
# /configuration
# /valid_locations
# /recent
# /summary_books_read_by_year
# /summary_books_read_by_year/2022
# /books_read
# /books_read/2022
# /status_read/1873
# /books_search
# /complete_records_window/1873/20
# /complete_record/1873
# /tag_counts
# /tag_counts/fiction
# /tags/1873
# /tags_search/Lewis
# /tag_maintenance
# /date_page_records/50
# /record_set/1873
# /image/year_progress_comparison.png
# /image/year_progress_comparison.png/20
# /image/all_years.png
# /image/all_years.png/2020


# Getting all of the PUT endpoints from book_service/books/api.py
# /add_tag/1873/fiction
# /update_tag_value/recovery/recovery
# /add_book_estimate/1873/15000
# /add_book_estimate/1873/15000/1945-10-19


```

## Curl Examples

List of Authors of unrecycled books in alphabetical order:
```angular2html
curl -H "x-api-key: sdf876a234hqkajsdv9876x87ehruia76df" \
http://172.17.0.2:8083/books_search?Recycled=0 | jq .data[][1]
```

Add books:
```angular2html
curl -X POST -H "Content-type: application/json" \
-H "x-api-key: sdf876a234hqkajsdv9876x87ehruia76df" \
-d @./examples/test_add_book.json \
http://172.17.0.2:8083/add_books
```

Update a book:
```angular2html
curl -X POST -H "Content-type: application/json" \
-H "x-api-key: sdf876a234hqkajsdv9876x87ehruia76df" \
-d @./examples/test_update_book.json \
http://172.17.0.2:8083/update_book
```


FAILED TO OPEN COLLECTION ERROR

```angular2html
The currently activated Python version 3.9.10 is not supported by the project (3.8.12).
Trying to find and use a compatible version. 
Using python3 (3.8.12)
Updating dependencies
Resolving dependencies... (0.4s)

Failed to unlock the collection!
scott@scott-pi-desktop:~/Working/php_books_database/tools/book_service$ export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring
```
