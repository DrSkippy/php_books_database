
Basic API usage:
```
http://172.17.0.2:8083/configuration
http://172.17.0.2:8083/tag_counts/
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


Deployment
```
kubectl apply -f deployment.yaml 
kubectl apply -f ingress.yaml 
kubectl expose deployment book-service --type=LoadBalancer --port=8083
```

API in K8s:
```
curl -kL https://192.168.127.7/books/configuration
curl -kL https://192.168.127.7/books/books-read-by-year
curl -kL https://192.168.127.7/books/tag_count
curl -kL https://192.168.127.7/books/tags/2
curl -kL https://192.168.127.7/books/books?Recycled=0
```

## BUILD and DEPLOY

```angular2html
docker build -t localhost:32000/book-service .
docker push localhost:32000/book-service
```
