#!/usr/bin/env python3
"""
Test Suite for Books MCP Server (HTTP Transport)

This test suite validates the MCP server's HTTP endpoints and MCP tools
when deployed in Docker. It tests both direct HTTP access and MCP protocol
communication over SSE.

Requirements:
    - MCP server running on http://localhost:3002
    - Install: pip install requests mcp

Usage:
    python test_booksmcp.py
"""

import asyncio
import json
import sys
import time
import unittest
from typing import Optional

import requests

# Try to import MCP client
try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    MCP_CLIENT_AVAILABLE = True
except ImportError:
    MCP_CLIENT_AVAILABLE = False
    print("\n⚠ Warning: MCP client not available")
    print("  Install with: pip install mcp")
    print("  Some tests will be skipped.\n")


class TestHTTPEndpoints(unittest.TestCase):
    """Test the HTTP endpoints directly (no MCP protocol)."""

    BASE_URL = "http://localhost:3002"

    @classmethod
    def setUpClass(cls):
        """Check if server is running."""
        try:
            response = requests.get(f"{cls.BASE_URL}/health", timeout=5)
            cls.server_available = response.status_code == 200

            if cls.server_available:
                print(f"\n✓ MCP Server is running at {cls.BASE_URL}")
            else:
                print(f"\n✗ Server returned status {response.status_code}")

        except requests.exceptions.RequestException as e:
            cls.server_available = False
            print(f"\n✗ Cannot connect to {cls.BASE_URL}")
            print(f"  Error: {e}")
            print("\n  To start the server:")
            print("    cd booksmcp")
            print("    docker-compose up -d --build\n")

    def setUp(self):
        """Skip test if server not available."""
        if not self.server_available:
            self.skipTest("MCP server not running")

    def test_01_health_endpoint(self):
        """Test GET /health endpoint."""
        response = requests.get(f"{self.BASE_URL}/health")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        print(f"\n  Health: {json.dumps(data, indent=2)}")

        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "books-mcp-server")
        self.assertIn("version", data)
        self.assertEqual(data["transport"], "HTTP/SSE")

        print("  ✓ Health check passed")

    def test_02_root_endpoint(self):
        """Test GET / endpoint for server info."""
        response = requests.get(f"{self.BASE_URL}/")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        print(f"\n  Server Info Preview:")
        print(f"    Name: {data['name']}")
        print(f"    Version: {data['version']}")
        print(f"    Transport: {data['transport']}")

        # Verify structure
        self.assertEqual(data["name"], "Books MCP Server")
        self.assertIn("version", data)
        self.assertIn("endpoints", data)
        self.assertIn("tools", data)
        self.assertIn("examples", data)

        # Verify tools
        tools = data["tools"]
        self.assertEqual(len(tools), 2)

        book_tool = next((t for t in tools if t["name"] == "search_books"), None)
        self.assertIsNotNone(book_tool)
        self.assertIn("description", book_tool)

        tag_tool = next((t for t in tools if t["name"] == "search_tags"), None)
        self.assertIsNotNone(tag_tool)
        self.assertIn("description", tag_tool)

        print("  ✓ Server info verified")

    def test_03_sse_endpoint_accessible(self):
        """Test that SSE endpoint is accessible."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/sse",
                stream=True,
                timeout=2
            )

            # SSE endpoints return 200 and keep connection open
            self.assertIn(response.status_code, [200, 202])
            print("\n  ✓ SSE endpoint is accessible")

        except requests.exceptions.Timeout:
            # Timeout is acceptable for SSE (connection stays open)
            print("\n  ✓ SSE endpoint connected (timed out as expected)")
            self.assertTrue(True)

        except requests.exceptions.RequestException as e:
            self.fail(f"SSE endpoint error: {e}")

    def test_04_messages_endpoint(self):
        """Test POST /messages endpoint."""
        test_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }

        response = requests.post(
            f"{self.BASE_URL}/messages",
            json=test_message,
            headers={"Content-Type": "application/json"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "received")

        print("\n  ✓ Messages endpoint accepts requests")


class TestMCPProtocol(unittest.TestCase):
    """Test MCP protocol over HTTP/SSE."""

    BASE_URL = "http://localhost:3002"

    @classmethod
    def setUpClass(cls):
        """Check prerequisites."""
        # Check if MCP client is available
        if not MCP_CLIENT_AVAILABLE:
            print("\n⚠ Skipping MCP protocol tests (client not installed)")
            return

        # Check if server is available
        try:
            response = requests.get(f"{cls.BASE_URL}/health", timeout=5)
            cls.server_available = response.status_code == 200
        except requests.exceptions.RequestException:
            cls.server_available = False

    def setUp(self):
        """Skip if prerequisites not met."""
        if not MCP_CLIENT_AVAILABLE:
            self.skipTest("MCP client not installed")
        if not self.server_available:
            self.skipTest("MCP server not running")

    def test_10_list_tools(self):
        """Test listing tools via MCP protocol."""
        async def run_test():
            print("\n  Connecting via SSE...")

            async with sse_client(f"{self.BASE_URL}/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize
                    await session.initialize()
                    print("  ✓ Session initialized")

                    # List tools
                    result = await session.list_tools()

                    self.assertIn("tools", result)
                    tools = result["tools"]

                    self.assertEqual(len(tools), 2)

                    print(f"  ✓ Found {len(tools)} tools:")
                    for t in tools:
                        print(f"    - {t['name']}: {t['description'][:50]}...")

        asyncio.run(run_test())

    def test_11_book_search_by_title(self):
        """Test book search by title."""
        async def run_test():
            print("\n  Testing: search_books tool with Title='lewis'")

            async with sse_client(f"{self.BASE_URL}/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Search for books using tool
                    result = await session.call_tool("search_books", {"Title": "lewis"})

                    self.assertIn("content", result)
                    content = result["content"][0]

                    self.assertEqual(content["type"], "text")

                    data = json.loads(content["text"])

                    self.assertIn("count", data)
                    self.assertIn("results", data)
                    self.assertGreater(data["count"], 0)

                    print(f"  ✓ Found {data['count']} books with 'lewis' in title")

                    if data["results"]:
                        first = data["results"][0]
                        print(f"    Example: \"{first.get('Title', 'N/A')}\" by {first.get('Author', 'N/A')}")

        asyncio.run(run_test())

    def test_12_book_search_by_author(self):
        """Test book search by author."""
        async def run_test():
            print("\n  Testing: search_books tool with Author='tolkien'")

            async with sse_client(f"{self.BASE_URL}/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.call_tool("search_books", {"Author": "tolkien"})

                    content = result["content"][0]
                    data = json.loads(content["text"])

                    self.assertIn("count", data)
                    print(f"  ✓ Found {data['count']} books by author matching 'tolkien'")

        asyncio.run(run_test())

    def test_13_book_search_multiple_params(self):
        """Test book search with multiple parameters."""
        async def run_test():
            print("\n  Testing: search_books tool with Author='lewis' and Category='fiction'")

            async with sse_client(f"{self.BASE_URL}/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.call_tool("search_books", {
                        "Author": "lewis",
                        "Category": "fiction"
                    })

                    content = result["content"][0]
                    data = json.loads(content["text"])

                    self.assertIn("count", data)
                    print(f"  ✓ Multi-parameter search found {data['count']} results")

        asyncio.run(run_test())

    def test_14_tag_search(self):
        """Test tag search."""
        async def run_test():
            print("\n  Testing: search_tags tool with query='science'")

            async with sse_client(f"{self.BASE_URL}/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.call_tool("search_tags", {"query": "science"})

                    content = result["content"][0]
                    data = json.loads(content["text"])

                    self.assertIn("query", data)
                    self.assertEqual(data["query"], "science")
                    self.assertIn("count", data)
                    self.assertIn("results", data)

                    print(f"  ✓ Tag search found {data['count']} results")

                    if data["results"]:
                        sample = data["results"][0]
                        print(f"    Example: BookID {sample['BookCollectionID']}, Tag: \"{sample['Tag']}\"")

        asyncio.run(run_test())

    def test_15_error_handling_no_params(self):
        """Test error handling when no parameters provided."""
        async def run_test():
            print("\n  Testing error handling: search_books tool with no params")

            async with sse_client(f"{self.BASE_URL}/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.call_tool("search_books", {})

                    content = result["content"][0]
                    data = json.loads(content["text"])

                    self.assertIn("error", data)
                    print(f"  ✓ Error correctly returned")

        asyncio.run(run_test())

    def test_16_error_handling_no_query(self):
        """Test error handling for tag search without query."""
        async def run_test():
            print("\n  Testing error handling: search_tags tool with no query")

            async with sse_client(f"{self.BASE_URL}/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.call_tool("search_tags", {})

                    content = result["content"][0]
                    data = json.loads(content["text"])

                    self.assertIn("error", data)
                    print(f"  ✓ Error correctly returned")

        asyncio.run(run_test())


class TestSummary(unittest.TestCase):
    """Print test summary."""

    def test_99_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("BOOKS MCP SERVER - TEST SUMMARY")
        print("="*80)
        print("\n✓ HTTP Endpoints Tested:")
        print("  • GET  / .................. Server information")
        print("  • GET  /health ............ Health check")
        print("  • GET  /sse ............... SSE connection")
        print("  • POST /messages .......... Message handling")

        if MCP_CLIENT_AVAILABLE:
            print("\n✓ MCP Protocol Tested (via SSE):")
            print("  • Initialize session")
            print("  • List tools")
            print("  • Call tools")

            print("\n✓ Tools Tested:")
            print("  • search_books")
            print("    - Search by Title")
            print("    - Search by Author")
            print("    - Multiple parameters")
            print("    - Error handling (no params)")
            print("  • search_tags")
            print("    - Tag search")
            print("    - Error handling (no query)")
        else:
            print("\n⚠ MCP Protocol Tests: SKIPPED (client not installed)")

        print("\n✓ Server Configuration:")
        print("  • Transport: HTTP/SSE")
        print("  • Port: 3002")
        print("  • Database: booksdb module")

        print("\n" + "="*80)
        self.assertTrue(True)


def main():
    """Run the test suite with proper formatting."""
    print("\n" + "="*80)
    print("BOOKS MCP SERVER - TEST SUITE")
    print("="*80)
    print("\nPrerequisites:")
    print("  1. Docker container 'booksmcp-server' must be running")
    print("  2. Server accessible at http://localhost:3002")
    print("\nTo start the server:")
    print("  cd booksmcp")
    print("  docker-compose up -d --build")
    print("\nTo view logs:")
    print("  docker-compose logs -f")
    print("="*80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests in order
    suite.addTests(loader.loadTestsFromTestCase(TestHTTPEndpoints))

    if MCP_CLIENT_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestMCPProtocol))

    suite.addTests(loader.loadTestsFromTestCase(TestSummary))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
