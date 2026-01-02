#!/bin/bash

# Deployment script for PHP Books Database Application
# This script deploys the production application to a remote webserver

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - Edit these variables for your deployment
REMOTE_USER="${DEPLOY_USER:-your_username}"
REMOTE_HOST="${DEPLOY_HOST:-your_server.com}"
REMOTE_PATH="${DEPLOY_PATH:-/var/www/html/books}"
SSH_PORT="${DEPLOY_SSH_PORT:-22}"

# Get the project root directory (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${GREEN}=== PHP Books Database Deployment Script ===${NC}"
echo "Project root: $PROJECT_ROOT"
echo "Target: $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
echo ""

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy the PHP Books Database application to a remote webserver.

OPTIONS:
    -h, --help          Show this help message
    -u, --user          Remote SSH username (default: \$DEPLOY_USER or 'your_username')
    -H, --host          Remote server hostname (default: \$DEPLOY_HOST or 'your_server.com')
    -p, --path          Remote deployment path (default: \$DEPLOY_PATH or '/var/www/html/books')
    -P, --port          SSH port (default: \$DEPLOY_SSH_PORT or 22)
    -d, --dry-run       Perform a dry run (show what would be deployed)

ENVIRONMENT VARIABLES:
    DEPLOY_USER         Remote SSH username
    DEPLOY_HOST         Remote server hostname
    DEPLOY_PATH         Remote deployment path
    DEPLOY_SSH_PORT     SSH port number

EXAMPLES:
    # Using command line arguments
    $0 -u webuser -H example.com -p /var/www/books

    # Using environment variables
    export DEPLOY_USER=webuser
    export DEPLOY_HOST=example.com
    export DEPLOY_PATH=/var/www/books
    $0

    # Dry run to see what will be deployed
    $0 --dry-run

EOF
    exit 1
}

# Parse command line arguments
DRY_RUN=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -u|--user)
            REMOTE_USER="$2"
            shift 2
            ;;
        -H|--host)
            REMOTE_HOST="$2"
            shift 2
            ;;
        -p|--path)
            REMOTE_PATH="$2"
            shift 2
            ;;
        -P|--port)
            SSH_PORT="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN="--dry-run"
            echo -e "${YELLOW}DRY RUN MODE - No files will be transferred${NC}"
            shift
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            ;;
    esac
done

# Validate configuration
if [ "$REMOTE_USER" = "your_username" ] || [ "$REMOTE_HOST" = "your_server.com" ]; then
    echo -e "${RED}Error: Please configure deployment settings${NC}"
    echo "Either:"
    echo "  1. Edit the script and set REMOTE_USER, REMOTE_HOST, and REMOTE_PATH"
    echo "  2. Set environment variables DEPLOY_USER, DEPLOY_HOST, DEPLOY_PATH"
    echo "  3. Use command line arguments: -u username -H hostname -p path"
    echo ""
    usage
fi

# Check if rsync is installed
if ! command -v rsync &> /dev/null; then
    echo -e "${RED}Error: rsync is not installed. Please install rsync first.${NC}"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

# Generate a new API key
echo -e "${GREEN}Generating new API key...${NC}"
NEW_API_KEY=$(openssl rand -hex 20)  # Generates a 40-character hex string
echo -e "${YELLOW}New API Key: ${NEW_API_KEY}${NC}"
echo ""

# Backup library/base.js and update with new API key
BASE_JS_FILE="$PROJECT_ROOT/library/base.js"
BASE_JS_BACKUP="$PROJECT_ROOT/library/base.js.backup"

if [ -z "$DRY_RUN" ]; then
    echo -e "${GREEN}Updating API key in library/base.js...${NC}"
    # Create backup
    cp "$BASE_JS_FILE" "$BASE_JS_BACKUP"

    # Replace the first line with the new API key
    NEW_FIRST_LINE="const apiKey = '${NEW_API_KEY}'; // FIRST LINE: Replace with your actual API key"
    sed -i "1s|.*|$NEW_FIRST_LINE|" "$BASE_JS_FILE"
    echo "API key updated in library/base.js"
    echo ""
fi

# Cleanup function to restore original file
cleanup() {
    if [ -f "$BASE_JS_BACKUP" ]; then
        echo -e "${YELLOW}Restoring original library/base.js...${NC}"
        mv "$BASE_JS_BACKUP" "$BASE_JS_FILE"
    fi
}

# Set trap to ensure cleanup happens even if script fails
trap cleanup EXIT

echo -e "${GREEN}Starting deployment...${NC}"
echo ""

# Deploy using rsync
rsync -avz $DRY_RUN \
    --delete \
    -e "ssh -p $SSH_PORT" \
    --include='*.php' \
    --include='*.ico' \
    --include='*.html' \
    --include='*.htm' \
    --include='js_reports/***' \
    --include='library/***' \
    --include='style/***' \
    --exclude='tools/' \
    --exclude='img/' \
    --exclude='*.md' \
    --exclude='README*' \
    --exclude='*README*' \
    --exclude='*.example' \
    --exclude='*example*' \
    --exclude='.git/' \
    --exclude='.gitignore' \
    --exclude='.gitattributes' \
    --exclude='.idea/' \
    --exclude='*.pyc' \
    --exclude='__pycache__/' \
    --exclude='.python-version' \
    --exclude='*.log' \
    --exclude='.env' \
    --exclude='.envrc' \
    --exclude='node_modules/' \
    --exclude='vendor/' \
    --exclude='.DS_Store' \
    ./ \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"

if [ -z "$DRY_RUN" ]; then
    echo ""
    echo -e "${GREEN}=== Deployment Complete ===${NC}"
    echo -e "Application deployed to: ${GREEN}$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH${NC}"
    echo ""
    echo -e "${GREEN}=== API Key Configuration ===${NC}"
    echo -e "${YELLOW}New API Key Generated: ${NEW_API_KEY}${NC}"
    echo ""
    echo -e "${GREEN}To configure the backend API service:${NC}"
    echo ""
    echo "1. Update the Dockerfile at tools/book_service/books/Dockerfile"
    echo "   Add this line after line 29 (after BOOKSDB_CONFIG):"
    echo ""
    echo -e "   ${YELLOW}ENV API_KEY=${NEW_API_KEY}${NC}"
    echo ""
    echo "2. Or set it at runtime using docker-compose.yml:"
    echo ""
    echo "   environment:"
    echo -e "     - ${YELLOW}API_KEY=${NEW_API_KEY}${NC}"
    echo ""
    echo "3. Or pass it when running the container:"
    echo ""
    echo -e "   ${YELLOW}docker run -e API_KEY=${NEW_API_KEY} ...${NC}"
    echo ""
    echo "4. Rebuild and restart the book_service/books container:"
    echo ""
    echo "   cd tools/book_service"
    echo "   docker-compose build books"
    echo "   docker-compose up -d books"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "  1. Update and rebuild the backend container with the new API key"
    echo "  2. Verify file permissions on the remote server"
    echo "  3. Check database configuration (db_header.php)"
    echo "  4. Test the application in your browser"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Save this API key securely!${NC}"
else
    echo ""
    echo -e "${YELLOW}=== Dry Run Complete ===${NC}"
    echo "No files were transferred. Run without --dry-run to deploy."
    echo ""
    echo -e "${YELLOW}Generated API Key (for reference): ${NEW_API_KEY}${NC}"
    echo "This key would be used to update library/base.js during actual deployment."
fi
