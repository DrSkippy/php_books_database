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

## BUILD and TEST

On OSX: 
```angular2html
docker build . -t book_service
docker run -p 127.0.0.1:80:8083 book_service
http://localhost/configuration
```
## BUILD and DEPLOY to K8s

```angular2html
docker build -t localhost:32000/book-service .
docker push localhost:32000/book-service
```

### Deployment to K8s
```
kubectl apply -f deployment.yaml 
kubectl apply -f ingress.yaml 
kubectl expose deployment book-service --type=LoadBalancer --port=8083
```

### Updated Image on K8s

```angular2html
kubectl rollout restart deployment/book-service
```

## Deploy to Linux Desktop

In base.js, set

```
const baseApiUrl = "http://192.168.127.166:8083";
```

Edit configuration.json to point to the MySQL server

## On Ubuntu Desktop, using docker-compose

2023-11-24 moved from Raspberry Pi to Ubuntu Desktop.

```
scott@lambda-dual:/opt/joplin$ cat joplin-docker-compose.yaml 
version: '3'

services:

    books:
        restart: unless-stopped
        image: book-service:latest
        ports:
            - "8083:8083"
        extra_hosts:
            - "host.docker.internal:host-gateway"

...

