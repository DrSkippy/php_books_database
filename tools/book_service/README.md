
Basic API usage:
```
http://172.17.0.2:5000/configuration
http://172.17.0.2:5000/tag_counts/
http://172.17.0.2:5000/tag_counts/science
http://172.17.0.2:5000/tags/2
http://172.17.0.2:5000/books_read_by_year
http://172.17.0.2:5000/books_read_by_year/2016
http://172.17.0.2:5000/books_read
http://172.17.0.2:5000/books_read/2016
http://172.17.0.2:5000/books
http://172.17.0.2:5000/books?Author=john
http://172.17.0.2:5000/books?Recycled=0
```

List of Authors of unrecycled books in alphabetical order:
```angular2html
curl http://172.17.0.2:5000/books?Recycled=0 | jq .data[][1]

```

Add books:
```angular2html
curl -X POST -H "Content-type: application/json" \ 
-d @./examples/test_add_book.json \
http://172.17.0.2:5000/add_books
```

Update a book:
```angular2html
curl -X POST -H "Content-type: application/json" \
-d @./examples/test_update_book.json \
http://172.17.0.2:5000/update_book
```