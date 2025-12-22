#!/usr/bin/env python3
"""
Books MCP Server - Streamable HTTP Transport

A Model Context Protocol (MCP) server that exposes book and tag search
functionality over HTTP using FastMCP and streamable HTTP transport.

This server provides two main tools:
1. search_books - Search books by various criteria (Title, Author, ISBN, etc.)
2. search_tags - Search books by tag labels

The server runs on port 3002 and uses streamable HTTP for MCP communication.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path to import booksdb
sys.path.insert(0, str(Path(__file__).parent.parent))

from booksdb import api_util
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP server with streamable HTTP support
port = int(os.getenv("PORT", "3002"))
host = os.getenv("HOST", "0.0.0.0")
mcp = FastMCP(
    "booksmcp-service",
    dependencies=["pymysql", "numpy"],
    host=host,
    port=port
)


# ============================================================================
# MCP Tool: Search Books
# ============================================================================

@mcp.tool()
def search_books(
        Title: str = None,
        Author: str = None,
        ISBNNumber: str = None,
        ISBNNumber13: str = None,
        PublisherName: str = None,
        Category: str = None,
        Location: str = None,
        Tags: str = None,
        ReadDate: str = None
) -> str:
    """
    Search books by title, author, ISBN, or other fields.

    Supports searching across multiple fields:
    - Title: Book title to search for
    - Author: Author name to search for
    - ISBNNumber: ISBN-10 number
    - ISBNNumber13: ISBN-13 number
    - PublisherName: Publisher name
    - Category: Book category
    - Location: Book location
    - Tags: Tags associated with the book
    - ReadDate: Date when the book was read

    Returns:
        JSON string with search results including count and book details
    """
    logger.info(f"Book search called with params: Title={Title}, Author={Author}, "
                f"ISBN={ISBNNumber}, ISBN13={ISBNNumber13}, Publisher={PublisherName}, "
                f"Category={Category}, Location={Location}, Tags={Tags}, ReadDate={ReadDate}")

    # Build parameters dictionary
    params = {}
    if Title is not None:
        params["Title"] = Title
    if Author is not None:
        params["Author"] = Author
    if ISBNNumber is not None:
        params["ISBNNumber"] = ISBNNumber
    if ISBNNumber13 is not None:
        params["ISBNNumber13"] = ISBNNumber13
    if PublisherName is not None:
        params["PublisherName"] = PublisherName
    if Category is not None:
        params["Category"] = Category
    if Location is not None:
        params["Location"] = Location
    if Tags is not None:
        params["Tags"] = Tags
    if ReadDate is not None:
        params["ReadDate"] = ReadDate

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


# ============================================================================
# MCP Tool: Search Tags
# ============================================================================

@mcp.tool()
def search_tags(query: str) -> str:
    """
    Search for books by tag labels.

    Args:
        query: Tag name to search for

    Returns:
        JSON string with search results including count and tagged books
    """
    logger.info(f"Tag search called with query: {query}")

    if not query:
        return json.dumps({
            "error": "No search query provided. Usage: provide a tag name to search for",
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
# Server Information Endpoint
# ============================================================================

@mcp.custom_route("/info", methods=['GET'])
async def server_info(request: Request) -> dict[str, Any]:
    """
    Provide server information.

    Returns:
        Dictionary with server metadata and available tools
    """
    return JSONResponse({
        "name": "Books MCP Server",
        "version": "2.0.0",
        "description": "MCP server for book and tag search functionality",
        "transport": "Streamable HTTP (FastMCP)",
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


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Start the MCP server with streamable HTTP transport."""

    logger.info("=" * 70)
    logger.info("Starting Books MCP Server (FastMCP)")
    logger.info("=" * 70)
    logger.info(f"Server: http://{host}:{port}")
    logger.info(f"Transport: Streamable HTTP")
    logger.info("")
    logger.info("Endpoints:")
    logger.info(f"  GET  http://{host}:{port}/health - Health check")
    logger.info(f"  GET  http://{host}:{port}/info   - Server information")
    logger.info(f"  *    http://{host}:{port}/mcp    - MCP protocol endpoint")
    logger.info("")
    logger.info("Tools:")
    logger.info("  search_books - Search books by title, author, ISBN, etc.")
    logger.info("  search_tags  - Search books by tag labels")
    logger.info("=" * 70)

    # Run with streamable HTTP transport
    mcp.run(
        transport="streamable-http"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
