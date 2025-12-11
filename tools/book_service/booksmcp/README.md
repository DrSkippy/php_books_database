# Books MCP Server

**HTTP-accessible MCP server for book and tag search functionality**

A Model Context Protocol (MCP) server that exposes book database search capabilities over HTTP using Server-Sent
Events (SSE) transport. Built with standard Python MCP packages and deployed via Docker on port 3002.

## Overview

This MCP server provides two main resources that wrap the existing `booksdb` module:

1. **`books://search`** - Search books by various criteria
2. **`tags://search`** - Search books by tag labels

The server uses HTTP/SSE transport, making it accessible via standard HTTP clients and MCP clients that support SSE.

## Features

✅ **HTTP Transport** - Accessible via HTTP on port 3002
✅ **SSE Protocol** - MCP communication over Server-Sent Events
✅ **Standard MCP** - Uses official Python MCP packages
✅ **Docker Deployment** - Containerized with Docker Compose
✅ **Database Integration** - Reuses existing `booksdb` module
✅ **Health Checks** - Built-in health monitoring
✅ **Resource Discovery** - MCP resource listing support

## Architecture

```
booksmcp/
├── __init__.py          # Package initialization
├── server.py            # MCP server with HTTP/SSE transport
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker container definition
├── docker-compose.yml  # Docker Compose configuration
└── README.md           # This file

Dependencies:
├── booksdb/            # Database utility module (reused)
└── config/             # Database configuration
```

## Resources

### 1. Book Search Resource

**URI:** `books://search?<parameters>`

Search books using various criteria. Multiple parameters can be combined.

**Supported Parameters:**

- `Title` - Book title (partial match)
- `Author` - Author name (partial match)
- `ISBNNumber` - ISBN-10
- `ISBNNumber13` - ISBN-13
- `PublisherName` - Publisher name
- `Category` - Book category
- `Location` - Physical location
- `Tags` - Tag labels
- `ReadDate` - Date when book was read

**Examples:**

```
books://search?Title=lewis
books://search?Author=tolkien
books://search?Tags=science
books://search?Author=lewis&Category=fiction
```

**Response Format:**

```json
{
  "query": {
    "Title": "lewis"
  },
  "count": 5,
  "results": [
    {
      "BookCollectionID": 155,
      "Title": "Letters To Children",
      "Author": "Lewis, C S",
      "CopyrightDate": "1985-01-01",
      "ISBNNumber": "0020861206",
      "PublisherName": "Macmillan Publishing Company",
      "CoverType": "hardcover",
      "Pages": 120,
      "Category": "Non-Fiction",
      "Note": null,
      "Recycled": 0,
      "Location": "Study",
      "ISBNNumber13": null,
      "ReadDate": "1966-01-15"
    }
  ]
}
```

### 2. Tag Search Resource

**URI:** `tags://search?<tag_name>`

Search for books by tag labels. Returns all books that have tags matching the search term.

**Examples:**

```
tags://search?science
tags://search?history
tags://search?fiction
```

**Response Format:**

```json
{
  "query": "science",
  "count": 12,
  "results": [
    {
      "BookCollectionID": 234,
      "TagID": 5,
      "Tag": "science fiction"
    }
  ]
}
```

## HTTP Endpoints

### GET /

Server information, available endpoints, resources, and usage examples.

```bash
curl http://localhost:3002/
```

### GET /health

Health check endpoint for monitoring.

```bash
curl http://localhost:3002/health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "books-mcp-server",
  "version": "1.0.0",
  "transport": "HTTP/SSE",
  "port": 3002
}
```

### GET /sse

SSE endpoint for MCP protocol communication. This is where MCP clients connect.

```bash
curl -N http://localhost:3002/sse
```

### POST /messages

Endpoint for receiving MCP messages from clients.

```bash
curl -X POST http://localhost:3002/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "resources/list"}'
```

## Prerequisites

- Docker and Docker Compose
- Database configuration at `../config/configuration.json`
- MySQL books database accessible

## Configuration

The server requires a configuration file at `/app/config/configuration.json`:

```json
{
  "username": "db_user",
  "password": "db_password",
  "database": "books",
  "host": "localhost",
  "port": 3306,
  "api_key": "your-api-key",
  "isbn_com": {
    "url_isbn": "https://api.isbndb.com/book/",
    "key": "your-isbn-key"
  }
}
```

## Deployment

### Using Docker Compose (Recommended)

1. **Navigate to the directory:**
   ```bash
   cd tools/book_service/booksmcp
   ```

2. **Build and start:**
   ```bash
   docker-compose up -d --build
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Check health:**
   ```bash
   curl http://localhost:3002/health
   ```

5. **Stop the server:**
   ```bash
   docker-compose down
   ```

### Using Docker Directly

1. **Build the image:**
   ```bash
   cd tools/book_service
   docker build -t booksmcp:latest -f booksmcp/Dockerfile .
   ```

For production:

    ```aiignore
    docker build -t localhost:5000/booksmcp:latest -f booksmcp/Dockerfile .
    docker push localhost:5000/booksmcp:latest 
    ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name booksmcp-server \
     -p 3002:3002 \
     booksmcp:latest
   ```

3. **Check logs:**
   ```bash
   docker logs -f booksmcp-server
   ```

## Usage

### Testing with HTTP/curl

```bash
# Check server status
curl http://localhost:3002/health

# Get server information
curl http://localhost:3002/

# Connect to SSE endpoint
curl -N http://localhost:3002/sse
```

### Using MCP Client (Python)

Install the MCP client:

```bash
pip install mcp
```

Example usage:

```python
import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client


async def search_books():
    # Connect to the MCP server
    async with sse_client("http://localhost:3002/sse") as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # List available resources
            resources = await session.list_resources()
            print("Available resources:", resources)

            # Search for books by title
            result = await session.read_resource("books://search?Title=lewis")
            content = result["contents"][0]
            data = json.loads(content["text"])

            print(f"Found {data['count']} books:")
            for book in data["results"]:
                print(f"  - {book['Title']} by {book['Author']}")


# Run the async function
asyncio.run(search_books())
```

### MCP Client Examples

**List Resources:**

```python
resources = await session.list_resources()
```

**Search Books by Title:**

```python
result = await session.read_resource("books://search?Title=tolkien")
```

**Search Books by Multiple Criteria:**

```python
result = await session.read_resource("books://search?Author=lewis&Category=fiction")
```

**Search by Tags:**

```python
result = await session.read_resource("tags://search?science")
```

## Testing

### Run Test Suite

```bash
cd tools/book_service/test_books
python test_booksmcp.py
```

The test suite includes:

- HTTP endpoint tests (always run)
- MCP protocol tests (requires `pip install mcp`)
- Resource validation
- Error handling tests

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:3002/health

# Test server info
curl http://localhost:3002/ | jq .

# Test SSE connection
curl -N http://localhost:3002/sse
```

## Development

### Local Development (Without Docker)

1. **Install dependencies:**
   ```bash
   cd tools/book_service/booksmcp
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   cd ..
   python -m booksmcp.server
   ```

3. **Server will start on:**
   ```
   http://localhost:3002
   ```

### Project Structure

```
tools/book_service/
├── booksdb/              # Database utilities (reused)
│   ├── __init__.py
│   └── api_util.py      # books_search_utility, tags_search_utility
├── booksmcp/            # MCP server application
│   ├── __init__.py
│   ├── server.py        # Main server implementation
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── config/              # Configuration files
│   └── configuration.json
└── test_books/          # Test suites
    └── test_booksmcp.py
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs booksmcp

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

- Verify `config/configuration.json` has correct credentials
- Ensure MySQL is accessible from Docker container
- For local MySQL on macOS/Windows, use `host.docker.internal` as host

### Port Already in Use

```bash
# Check what's using port 3002
lsof -i :3002

# Change port in docker-compose.yml
ports:
  - "3003:3002"  # Map to different host port
```

### MCP Client Connection Issues

- Verify server is running: `curl http://localhost:3002/health`
- Check SSE endpoint: `curl -N http://localhost:3002/sse`
- Ensure MCP client is installed: `pip install mcp`

### Health Check Failing

```bash
# Check container health
docker ps

# View health check logs
docker inspect booksmcp-server | jq '.[0].State.Health'
```

## Dependencies

### Python Packages

- **mcp** (>=1.0.0) - Model Context Protocol SDK
- **uvicorn[standard]** (>=0.30.0) - ASGI server
- **starlette** (>=0.37.0) - Web framework
- **pymysql** (>=1.1.0) - MySQL connector
- **numpy** (>=1.24.0) - Numerical operations

### System Requirements

- Python 3.11+
- Docker 20.10+
- Docker Compose 2.0+

## Environment Variables

- `PORT` - Server port (default: 3002)
- `HOST` - Bind address (default: 0.0.0.0)
- `PYTHONUNBUFFERED` - Python output buffering (default: 1)

## Monitoring

### Health Checks

The server includes built-in health checks:

**Docker Health Check:**

```yaml
healthcheck:
  test: [ "CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:3002/health')" ]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Manual Health Check:**

```bash
curl http://localhost:3002/health
```

### Logs

```bash
# View real-time logs
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100

# View logs for specific container
docker logs booksmcp-server
```

## Performance

- **Resource caching:** Results are not cached; each request queries the database
- **Connection pooling:** Not implemented; uses direct database connections
- **Concurrent requests:** Supported via async/await

## Security

- Database credentials are mounted read-only
- No authentication on HTTP endpoints (add reverse proxy with auth if needed)
- SQL injection protection via parameterized queries in booksdb module

## License

Inherits license from the parent Books Database project.

## Contributing

When contributing:

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Test with Docker Compose before committing

## Support

For issues or questions:

1. Check this README
2. Review Docker logs: `docker-compose logs`
3. Run test suite: `python test_booksmcp.py`
4. Check server info: `curl http://localhost:3002/`

## Version History

- **1.0.0** - Initial release with HTTP/SSE transport
    - Books search resource
    - Tags search resource
    - Docker deployment
    - Health checks
    - Comprehensive test suite
