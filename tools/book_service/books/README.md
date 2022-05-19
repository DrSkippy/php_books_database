###Use Cases Supported:

1. Add book records
2. Update read date for a book
3. Resport on books/pages read by year
4. List books read by year
5. List books by read/recycled status in Alpha by Author
6. Update Note on book
7. Update recycled status
8. Add tags to book record
9. Search for books by tag


## BUILD and DEPLOY

```angular2html
docker build -t localhost:32000/book-service .
docker push localhost:32000/book-service
```

### Deployment
```
kubectl apply -f deployment.yaml 
kubectl apply -f ingress.yaml 
kubectl expose deployment book-service --type=LoadBalancer --port=8083
```

### Updated Image

```angular2html
kubectl rollout restart deployment/book-service
```