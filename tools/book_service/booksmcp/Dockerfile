FROM python:3.11-slim

LABEL maintainer="Books MCP Server"
LABEL description="MCP Server for Books Database with HTTP/SSE transport"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY booksmcp/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY booksdb/ /app/booksdb/
COPY booksmcp/ /app/booksmcp/
COPY config/ /app/config/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=3002
ENV HOST=0.0.0.0

# Expose port 3002 for HTTP access
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3002/health')"

# Run the MCP server
CMD ["python", "-m", "booksmcp.server"]
