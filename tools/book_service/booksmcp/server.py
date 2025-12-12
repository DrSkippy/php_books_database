#!/usr/bin/env python3
"""
Books MCP Server - HTTP Transport

A Model Context Protocol (MCP) server that exposes book and tag search
functionality over HTTP. This server uses the standard Python MCP packages
and provides two main tools:

1. search_books - Search books by various criteria (Title, Author, ISBN, etc.)
2. search_tags - Search books by tag labels

The server runs on port 3002 and uses HTTP/SSE for MCP communication.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path to import booksdb
sys.path.insert(0, str(Path(__file__).parent.parent))

from booksdb import api_util

# MCP imports
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

# HTTP server imports
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp_server = Server("books-mcp-server")


# ============================================================================
# MCP Tool Handlers
# ============================================================================

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available MCP tools.

    Returns:
        List of available tools (book search and tag search)
    """
    logger.info("Listing tools")
    return [
        Tool(
            name="search_books",
            description="Search books by title, author, ISBN, or other fields. "
                       "Supports parameters: Title, Author, ISBNNumber, ISBNNumber13, "
                       "PublisherName, Category, Location, Tags, ReadDate",
            inputSchema={
                "type": "object",
                "properties": {
                    "Title": {"type": "string", "description": "Book title to search for"},
                    "Author": {"type": "string", "description": "Author name to search for"},
                    "ISBNNumber": {"type": "string", "description": "ISBN-10 number"},
                    "ISBNNumber13": {"type": "string", "description": "ISBN-13 number"},
                    "PublisherName": {"type": "string", "description": "Publisher name"},
                    "Category": {"type": "string", "description": "Book category"},
                    "Location": {"type": "string", "description": "Book location"},
                    "Tags": {"type": "string", "description": "Tags associated with the book"},
                    "ReadDate": {"type": "string", "description": "Date when the book was read"}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="search_tags",
            description="Search for books by tag labels. Returns books with matching tags.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Tag name to search for"}
                },
                "required": ["query"],
                "additionalProperties": False
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Call a tool by name with the provided arguments.

    Args:
        name: Tool name ('search_books' or 'search_tags')
        arguments: Tool arguments as a dictionary

    Returns:
        List of TextContent with search results
    """
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    try:
        if name == "search_books":
            result = await handle_book_search(arguments)
        elif name == "search_tags":
            result = await handle_tag_search(arguments)
        else:
            result = json.dumps({
                "error": f"Unknown tool: {name}. Supported: search_books, search_tags",
                "results": []
            })

        return [TextContent(type="text", text=result)]
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        error_result = json.dumps({
            "error": str(e),
            "results": []
        })
        return [TextContent(type="text", text=error_result)]


async def handle_book_search(params: dict) -> str:
    """
    Handle book search requests.

    Args:
        params: Search parameters (Title, Author, etc.)

    Returns:
        JSON string with search results
    """
    logger.info(f"Book search with params: {params}")

    if not params:
        return json.dumps({
            "error": "No search parameters provided. Supported: Title, Author, "
                    "ISBNNumber, ISBNNumber13, PublisherName, Category, Location, Tags, ReadDate",
            "results": []
        })

    try:
        # Call the books_search_utility from booksdb
        data_rows, raw_data, header, error_list = api_util.books_search_utility(params)

        if error_list:
            return json.dumps({
                "query": params,
                "error": error_list,
                "results": []
            })

        # Convert results to list of dictionaries
        results = []
        if data_rows:
            for row in data_rows:
                book = {}
                for i, col_name in enumerate(header):
                    if i < len(row):
                        value = row[i]
                        # Convert datetime objects to strings
                        if hasattr(value, 'strftime'):
                            value = value.strftime("%Y-%m-%d")
                        book[col_name] = value
                results.append(book)

        return json.dumps({
            "query": params,
            "count": len(results),
            "results": results
        }, indent=2)

    except Exception as e:
        logger.error(f"Book search error: {e}", exc_info=True)
        return json.dumps({
            "query": params,
            "error": [str(e)],
            "results": []
        })


async def handle_tag_search(params: dict) -> str:
    """
    Handle tag search requests.

    Args:
        params: Search parameters (should contain 'query')

    Returns:
        JSON string with search results
    """
    # Extract search query
    query = params.get("query", "")

    logger.info(f"Tag search with query: {query}")

    if not query:
        return json.dumps({
            "error": "No search query provided. Usage: tags://search?<tag_name>",
            "results": []
        })

    try:
        # Call the tags_search_utility from booksdb
        data_rows, raw_data, header, error_list = api_util.tags_search_utility(query)

        if error_list:
            return json.dumps({
                "query": query,
                "error": error_list,
                "results": []
            })

        # Convert results to list of dictionaries
        results = []
        if data_rows:
            for row in data_rows:
                tag = {}
                for i, col_name in enumerate(header):
                    if i < len(row):
                        tag[col_name] = row[i]
                results.append(tag)

        return json.dumps({
            "query": query,
            "count": len(results),
            "results": results
        }, indent=2)

    except Exception as e:
        logger.error(f"Tag search error: {e}", exc_info=True)
        return json.dumps({
            "query": query,
            "error": [str(e)],
            "results": []
        })


# ============================================================================
# HTTP Endpoint Handlers
# ============================================================================

async def handle_root(request: Request) -> JSONResponse:
    """Handle GET / - Server information."""
    return JSONResponse({
        "name": "Books MCP Server",
        "version": "1.0.0",
        "description": "MCP server for book and tag search functionality",
        "transport": "HTTP/SSE",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "sse": "/sse",
            "messages": "/messages"
        },
        "tools": [
            {
                "name": "search_books",
                "description": "Search books by title, author, ISBN, category, tags, etc.",
                "parameters": ["Title", "Author", "ISBNNumber", "ISBNNumber13",
                             "PublisherName", "Category", "Location", "Tags", "ReadDate"]
            },
            {
                "name": "search_tags",
                "description": "Search books by tag labels",
                "parameters": ["query"]
            }
        ],
        "examples": {
            "book_by_title": {"tool": "search_books", "arguments": {"Title": "lewis"}},
            "book_by_author": {"tool": "search_books", "arguments": {"Author": "tolkien"}},
            "book_by_tags": {"tool": "search_books", "arguments": {"Tags": "science"}},
            "tag_search": {"tool": "search_tags", "arguments": {"query": "history"}}
        }
    })


async def handle_health(request: Request) -> JSONResponse:
    """Handle GET /health - Health check."""
    return JSONResponse({
        "status": "healthy",
        "service": "books-mcp-server",
        "version": "1.0.0",
        "transport": "HTTP/SSE",
        "port": int(os.getenv("PORT", "3002"))
    })


async def handle_sse(request: Request) -> Response:
    """
    Handle GET /sse - SSE endpoint for MCP communication.

    This endpoint establishes a Server-Sent Events connection for
    bidirectional MCP protocol communication.
    """
    logger.info(f"SSE connection request from {request.client.host}")

    # Create SSE transport
    sse = SseServerTransport("/messages")

    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

    # This line won't be reached during normal operation
    return Response(status_code=204)


async def handle_messages(request: Request) -> JSONResponse:
    """
    Handle POST /messages - Receive MCP messages.

    This endpoint receives messages sent by MCP clients.
    """
    try:
        body = await request.body()
        logger.info(f"Received message: {body.decode()}")

        # Parse the message
        message = json.loads(body.decode())

        return JSONResponse({
            "status": "received",
            "message_id": message.get("id")
        })

    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e)},
            status_code=400
        )


# ============================================================================
# Starlette Application
# ============================================================================

app = Starlette(
    debug=True,
    routes=[
        Route("/", handle_root, methods=["GET"]),
        Route("/health", handle_health, methods=["GET"]),
        Route("/sse", handle_sse, methods=["GET"]),
        Route("/messages", handle_messages, methods=["POST"]),
    ]
)


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Start the HTTP server."""
    port = int(os.getenv("PORT", "3002"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info("="*70)
    logger.info("Starting Books MCP Server")
    logger.info("="*70)
    logger.info(f"Server: http://{host}:{port}")
    logger.info(f"Transport: HTTP/SSE")
    logger.info("")
    logger.info("Endpoints:")
    logger.info(f"  GET  http://{host}:{port}/         - Server info")
    logger.info(f"  GET  http://{host}:{port}/health   - Health check")
    logger.info(f"  GET  http://{host}:{port}/sse      - SSE connection")
    logger.info(f"  POST http://{host}:{port}/messages - Messages")
    logger.info("")
    logger.info("Tools:")
    logger.info("  search_books - Search books by title, author, ISBN, etc.")
    logger.info("  search_tags  - Search books by tag labels")
    logger.info("="*70)

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
