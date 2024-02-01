### Use Cases Supported:

0. View configuration
1. Book locations
1. Add book records
2. Update read date for a book
3. Report on books/pages read by year
4. List books read by year
5. List books by read/recycled status in Alpha by Author
6. Update Note on book
7. Update recycled status
8. Add tags to book record
9. Search for books by tag

## BUILD and DEPLOY SERVICE for local testing

On OSX and Linux to run local tests: 
```angular2html
docker build . -t book-service
docker run -p 127.0.0.1:80:8083 book-service
```
```
curl -H "x-api-key: sdf876a234hqkajsdv9876x87ehruia76df" localhost/valid_locations
```

## BUILD and DEPLOY SERVICE to K8s

```angular2html
docker build -t localhost:32000/book-service .
docker push localhost:32000/book-service
```

### Deployment to K8s
```angular2html
kubectl apply -f deployment.yaml 
kubectl apply -f ingress.yaml 
kubectl expose deployment book-service --type=LoadBalancer --port=8083
```

### Updated Image on K8s

```angular2html
kubectl rollout restart deployment/book-service
```

## DEPLOY SERVICE to production, using docker-compose

2023-11-24 moved from Raspberry Pi to Ubuntu Desktop.

Configuration segment of docker-compose.yaml:

```
version: '3'

services:

    books:
        restart: unless-stopped
        image: book-service:latest
        ports:
            - "8083:8083"
        extra_hosts:
            - "host.docker.internal:host-gateway"
```

To deploy:

```angular2html
scott@lambda-dual:/opt/joplin$ docker-compose -f ./joplin-docker-compose.yaml up -d books
```
