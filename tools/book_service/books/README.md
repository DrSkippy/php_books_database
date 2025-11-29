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
docker build . -t book-test
docker run -p 127.0.0.1:9999:8083 book-test
```
```
curl -H "x-api-key: sdf876a234hqkajsdv9876x87ehruia76df" localhost/valid_locations
```

## BUILD and DEPLOY SERVICE with Portainer.io

Run a local registry in Portainer.io
```aiignore
version: '3.8'
services:
  registry:
    image: registry:2
    ports:
      - "5000:5000" # Map host port 5000 to container port 5000
    volumes:
      - ./data/registry:/var/lib/registry # Persist registry data
    restart: always # Ensure the registry restarts if it stops
```
Set insecure registry in /etc/docker/daemon.json
```aiignore
{
  "insecure-registries" : ["localhost:5000"]
}
```

Push to registry:

```
docker build . -t localhost:5000/book-service:latest
docker push localhost:5000/book-service:latest
curl localhost:5000/v2/_catalog
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
