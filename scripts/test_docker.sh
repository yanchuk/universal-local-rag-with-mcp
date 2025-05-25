#!/bin/bash

# Docker Compatibility Test Script
# Tests Docker Compose functionality across different macOS versions

set -e

echo "🐳 Testing Docker Compose Compatibility"
echo "======================================"

# Test basic Docker installation
echo ""
echo "1. Testing Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Test Docker daemon
echo ""
echo "2. Testing Docker daemon..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker daemon is running"

# Test Docker Compose commands
echo ""
echo "3. Testing Docker Compose commands..."

# Test modern Docker Compose (docker compose)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    COMPOSE_VERSION=$(docker compose version)
    echo "✅ Modern Docker Compose found: $COMPOSE_VERSION"
    MODERN_COMPOSE=true
else
    echo "❌ Modern Docker Compose (docker compose) not available"
    MODERN_COMPOSE=false
fi

# Test legacy Docker Compose (docker-compose)
if command -v docker-compose &> /dev/null; then
    LEGACY_COMPOSE_VERSION=$(docker-compose version --short)
    echo "✅ Legacy Docker Compose found: docker-compose $LEGACY_COMPOSE_VERSION"
    LEGACY_COMPOSE=true
    if [ "$MODERN_COMPOSE" = false ]; then
        COMPOSE_CMD="docker-compose"
    fi
else
    echo "❌ Legacy Docker Compose (docker-compose) not available"
    LEGACY_COMPOSE=false
fi

# Determine which command to use
echo ""
echo "4. Docker Compose compatibility summary:"
if [ "$MODERN_COMPOSE" = true ]; then
    echo "✅ Recommended: Use 'docker compose' (modern syntax)"
    COMPOSE_CMD="docker compose"
elif [ "$LEGACY_COMPOSE" = true ]; then
    echo "⚠️  Fallback: Use 'docker-compose' (legacy syntax)"
    COMPOSE_CMD="docker-compose"
else
    echo "❌ No Docker Compose found. Please update Docker Desktop."
    exit 1
fi

echo "   Command to use: $COMPOSE_CMD"

# Test basic functionality
echo ""
echo "5. Testing basic Docker Compose functionality..."

# Create a simple test compose file
cat > docker-compose.test.yml << EOF
version: '3.8'
services:
  test:
    image: hello-world
    container_name: rag-test-container
EOF

echo "   Testing compose file validation..."
if $COMPOSE_CMD -f docker-compose.test.yml config > /dev/null 2>&1; then
    echo "✅ Docker Compose file validation passed"
else
    echo "❌ Docker Compose file validation failed"
    rm -f docker-compose.test.yml
    exit 1
fi

echo "   Testing container lifecycle..."
if $COMPOSE_CMD -f docker-compose.test.yml up --no-log-prefix > /dev/null 2>&1; then
    echo "✅ Container startup test passed"
else
    echo "❌ Container startup test failed"
fi

# Cleanup
$COMPOSE_CMD -f docker-compose.test.yml down --remove-orphans > /dev/null 2>&1 || true
docker rm rag-test-container > /dev/null 2>&1 || true
rm -f docker-compose.test.yml

# Test ChromaDB compatibility
echo ""
echo "6. Testing ChromaDB container compatibility..."

# Create ChromaDB test
cat > docker-compose.chromadb-test.yml << EOF
version: '3.8'
services:
  chromadb-test:
    image: chromadb/chroma:0.4.24
    container_name: rag-chromadb-test
    ports:
      - "8001:8000"
    environment:
      - ANONYMIZED_TELEMETRY=False
      - IS_PERSISTENT=FALSE
EOF

echo "   Starting test ChromaDB instance..."
if $COMPOSE_CMD -f docker-compose.chromadb-test.yml up -d > /dev/null 2>&1; then
    echo "✅ ChromaDB container started successfully"
    
    # Wait a moment for startup
    echo "   Waiting for ChromaDB to be ready..."
    sleep 5
    
    # Test ChromaDB API
    if curl -f http://localhost:8001/api/v1/heartbeat > /dev/null 2>&1; then
        echo "✅ ChromaDB API is responding"
        CHROMADB_TEST_PASSED=true
    elif curl -f http://localhost:8001/ > /dev/null 2>&1; then
        echo "✅ ChromaDB is responding (alternative endpoint)"
        CHROMADB_TEST_PASSED=true
    else
        echo "⚠️  ChromaDB container started but API not responding"
        echo "   This may be normal if ChromaDB is still starting up"
        CHROMADB_TEST_PASSED=false
    fi
else
    echo "❌ ChromaDB container failed to start"
    CHROMADB_TEST_PASSED=false
fi

# Cleanup ChromaDB test
$COMPOSE_CMD -f docker-compose.chromadb-test.yml down --volumes > /dev/null 2>&1 || true
rm -f docker-compose.chromadb-test.yml

# Test port availability
echo ""
echo "7. Testing port availability..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use. You may need to stop other services."
    echo "   Run: lsof -i :8000 to see what's using the port"
else
    echo "✅ Port 8000 is available for ChromaDB"
fi

# System compatibility check
echo ""
echo "8. System compatibility check..."

# Check available memory
AVAILABLE_MEMORY_GB=$(python3 -c "
import psutil
memory = psutil.virtual_memory()
print(f'{memory.available / (1024**3):.1f}')
" 2>/dev/null || echo "unknown")

if [ "$AVAILABLE_MEMORY_GB" != "unknown" ]; then
    echo "   Available memory: ${AVAILABLE_MEMORY_GB}GB"
    if (( $(echo "$AVAILABLE_MEMORY_GB >= 2.0" | bc -l 2>/dev/null || echo 0) )); then
        echo "✅ Sufficient memory for RAG system"
    else
        echo "⚠️  Low memory. Consider closing other applications during setup"
    fi
else
    echo "   Memory check: Unable to determine available memory"
fi

# Check disk space
AVAILABLE_DISK_GB=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//' 2>/dev/null || echo "unknown")
if [ "$AVAILABLE_DISK_GB" != "unknown" ] && [ "$AVAILABLE_DISK_GB" -gt 4 ] 2>/dev/null; then
    echo "✅ Sufficient disk space for RAG system"
else
    echo "⚠️  Check available disk space (need ~4GB for embeddings and data)"
fi

# Final summary
echo ""
echo "🎉 Docker Compatibility Test Summary"
echo "===================================="
echo "Docker Command: $COMPOSE_CMD"
echo "Modern Compose: $MODERN_COMPOSE"
echo "Legacy Compose: $LEGACY_COMPOSE"
echo "ChromaDB Test: $CHROMADB_TEST_PASSED"
echo ""

if [ "$MODERN_COMPOSE" = true ] || [ "$LEGACY_COMPOSE" = true ]; then
    echo "✅ Your system is ready for Universal Organization RAG setup!"
    echo ""
    echo "Next steps:"
    echo "1. Create your config.yaml file"
    echo "2. Run: ./setup.sh"
    echo ""
    echo "The setup script will automatically use: $COMPOSE_CMD"
else
    echo "❌ Please install or update Docker Desktop before proceeding"
    exit 1
fi
