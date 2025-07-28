#!/bin/bash

# Universal Organization RAG Setup Script
# Configurable setup for any organization's documentation RAG system
# Optimized for cross-platform compatibility (macOS, Linux)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration file handling
CONFIG_FILE="config.yaml"
if [ "$1" ]; then
    CONFIG_FILE="$1"
fi

print_status "Starting Universal Organization RAG Setup..."
print_status "Using configuration: $CONFIG_FILE"

# Check if configuration file exists
if [ ! -f "$CONFIG_FILE" ]; then
    print_error "Configuration file not found: $CONFIG_FILE"
    print_error "Please create a config.yaml file or use one from config_examples/"
    print_error "Example: ./setup.sh config_examples/startup_company.yaml"
    exit 1
fi

# We'll extract the organization name after installing dependencies
print_status "Setting up RAG system..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create directories
print_status "Creating directories..."
mkdir -p chroma_data logs

# Setup Python virtual environment
print_status "Setting up Python virtual environment..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Created new virtual environment"
else
    print_status "Using existing virtual environment"
fi

source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip

# Install requirements with error handling
if pip install -r requirements.txt; then
    print_success "Python dependencies installed successfully"
else
    print_error "Failed to install Python dependencies"
    print_error "Check requirements.txt and try running: pip install -r requirements.txt"
    exit 1
fi

print_success "Python environment setup complete"

# Now extract organization name from config (after PyYAML is installed)
ORG_NAME=$(python3 -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    print(config.get('organization', {}).get('name', 'Unknown'))
except:
    print('Unknown')
")

print_status "Organization: $ORG_NAME"

# Start ChromaDB
print_status "Starting ChromaDB container..."

# Auto-detect Docker Compose command
if command -v docker &> /dev/null; then
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        print_error "Neither 'docker compose' nor 'docker-compose' found. Please install Docker Desktop."
        exit 1
    fi
else
    print_error "Docker not found. Please install Docker Desktop."
    exit 1
fi

print_status "Using Docker Compose command: $DOCKER_COMPOSE_CMD"
$DOCKER_COMPOSE_CMD down --remove-orphans 2>/dev/null || true
$DOCKER_COMPOSE_CMD up --build -d

# Wait for ChromaDB to be ready
print_status "Waiting for ChromaDB to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -f http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
        print_success "ChromaDB is ready!"
        break
    elif curl -f http://localhost:8000/api/v1/version > /dev/null 2>&1; then
        print_success "ChromaDB is ready!"
        break
    elif curl -f http://localhost:8000/ > /dev/null 2>&1; then
        print_success "ChromaDB is ready!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS - waiting for ChromaDB..."
    
    if [ $((ATTEMPT % 10)) -eq 0 ]; then
        echo "ChromaDB status check:"
        $DOCKER_COMPOSE_CMD ps
        echo "Recent ChromaDB logs:"
        $DOCKER_COMPOSE_CMD logs --tail=5 chromadb
    fi
    
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_error "ChromaDB failed to start within timeout. Check Docker logs:"
    $DOCKER_COMPOSE_CMD logs
    exit 1
fi

# Validate configuration and data paths
print_status "Validating configuration and data paths..."

python3 -c "
import yaml
import sys
from pathlib import Path

try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    
    # Check documentation path
    docs_path = config['data_sources']['documentation']['base_path']
    if not Path(docs_path).exists():
        print(f'ERROR: Documentation path not found: {docs_path}')
        sys.exit(1)
    
    # Check GitHub path if enabled
    if config['data_sources'].get('github', {}).get('enabled', False):
        github_path = config['data_sources']['github'].get('issues_path')
        if github_path and not Path(github_path).exists():
            print(f'WARNING: GitHub issues path not found: {github_path}')
            print('GitHub ingestion will be skipped')
    
    org_name = config['organization']['name']
    purpose = config['rag_goals']['primary_purpose']
    
    print(f'✓ Configuration valid for {org_name}')
    print(f'✓ Purpose: {purpose}')
    print(f'✓ Documentation path: {docs_path}')
    
except Exception as e:
    print(f'ERROR: Configuration validation failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    print_error "Configuration validation failed"
    exit 1
fi

print_success "Configuration validated"

# Run ingestion
print_status "Starting data ingestion process..."
print_status "Organization: $ORG_NAME"
print_status "This may take 15-45 minutes depending on your documentation size..."

python ingest_data.py "$CONFIG_FILE"

if [ $? -eq 0 ]; then
    print_success "Data ingestion completed successfully!"
else
    print_error "Data ingestion failed. Check the logs for details."
    exit 1
fi

# Check ChromaDB version compatibility
print_status "Checking ChromaDB version compatibility for MCP..."
if python scripts/check_versions.py; then
    print_success "ChromaDB versions are compatible"
else
    print_warning "ChromaDB version compatibility issues detected"
    print_warning "MCP integration may not work correctly"
    print_warning "Run 'python scripts/check_versions.py' for detailed fixes"
fi

# Extract collection name and show final status
COLLECTION_NAME=$(python3 -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    org_name = config['organization']['name'].lower().replace(' ', '_')
    base_name = config['chromadb']['collection_name']
    print(f'{org_name}_{base_name}')
except:
    print('organization_knowledge')
")

print_status "Getting collection statistics..."
curl -s "http://localhost:8000/api/v1/collections/$COLLECTION_NAME" | python3 -m json.tool 2>/dev/null || echo "Collection stats not available"

print_success "$ORG_NAME Knowledge Base Setup Complete!"
echo ""
echo "🎯 Your RAG System is Ready:"
echo "1. ChromaDB is running at http://localhost:8000"
echo "2. Collection name: $COLLECTION_NAME"
echo "3. Configuration: $CONFIG_FILE"
echo "4. Organization: $ORG_NAME"
echo ""
echo "💡 Test your setup:"
echo "   python test_setup.py $CONFIG_FILE"
echo ""
echo "🔧 Setup Claude Desktop MCP integration:"
echo "   python scripts/setup_mcp.py"
echo ""
echo "🔍 Query your knowledge base:"
echo "   Use the collection '$COLLECTION_NAME' in your applications"
echo ""
echo "⚙️  Management commands:"
echo "   Stop ChromaDB: $DOCKER_COMPOSE_CMD down"
echo "   Restart ChromaDB: $DOCKER_COMPOSE_CMD up -d"
echo "   View logs: $DOCKER_COMPOSE_CMD logs -f"
echo "   Re-ingest data: python ingest_data.py $CONFIG_FILE"
echo "   Check versions: python scripts/check_versions.py"
