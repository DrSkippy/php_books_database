
Basic API usage:
```
http://172.17.0.2:8083/configuration
http://172.17.0.2:8083/tag_counts
http://172.17.0.2:8083/tag_counts/science
http://172.17.0.2:8083/tags/2
http://172.17.0.2:8083/books_read_by_year
http://172.17.0.2:8083/books_read_by_year/2016
http://172.17.0.2:8083/books_read
http://172.17.0.2:8083/books_read/2016
http://172.17.0.2:8083/books
http://172.17.0.2:8083/books?Author=john
http://172.17.0.2:8083/books?Recycled=0
```

List of Authors of unrecycled books in alphabetical order:
```angular2html
curl http://172.17.0.2:8083/books?Recycled=0 | jq .data[][1]
```

Add books:
```angular2html
curl -X POST -H "Content-type: application/json" \
-d @./examples/test_add_book.json \
http://172.17.0.2:8083/add_books
```

Update a book:
```angular2html
curl -X POST -H "Content-type: application/json" \
-d @./examples/test_update_book.json \
http://172.17.0.2:8083/update_book
```

API in K8s:
```
curl -kL https://192.168.127.7/books/configuration
curl -kL https://192.168.127.7/books/books-read-by-year
curl -kL https://192.168.127.7/books/tag_count
curl -kL https://192.168.127.7/books/tags/2
curl -kL https://192.168.127.7/books/books?Recycled=0
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