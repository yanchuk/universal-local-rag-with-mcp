# Setup Guide

## Prerequisites

- **Docker Desktop** (must be running)
- **Python 3.8+**
- **4GB+ RAM** (8GB recommended)
- **2GB disk space**

## Installation

### 1. Clone and Configure

```bash
git clone https://github.com/yanchuk/universal-local-rag-with-mcp.git
cd universal-local-rag-with-mcp

# Choose a config template
cp config_examples/startup_company.yaml config.yaml
# Edit config.yaml with your organization details
```

### 2. Run Setup

```bash
# Auto-detects docker-compose vs docker compose
./setup.sh

# If permission denied:
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create Python virtual environment
- Install dependencies (including chroma-mcp)
- Start ChromaDB container
- Validate configuration
- Ingest your documentation

### 3. Test Installation

**⚠️ Always activate virtual environment first:**

```bash
# Activate virtual environment
source venv/bin/activate

# Windows users:
# venv\Scripts\activate

# Run comprehensive tests
python test_setup.py config.yaml
```

## Configuration

Edit `config.yaml` to match your organization:

```yaml
organization:
  name: "YourCompany"
  description: "Your company description"

data_sources:
  documentation:
    base_path: "/path/to/your/docs"
    priority_paths:
      - "handbook"
      - "team-docs"

target_teams:
  - name: "engineering"
    keywords: ["engineering", "development", "technical"]
  - name: "product"
    keywords: ["product", "pm", "roadmap"]

rag_goals:
  primary_purpose: "interview_preparation"  # or "knowledge_management", "onboarding"
```

See [Configuration Guide](CONFIGURATION.md) for detailed examples.

## Common Commands

### ChromaDB Management
```bash
# Start ChromaDB
docker compose up -d

# Stop ChromaDB  
docker compose down

# View logs
docker compose logs -f chromadb

# Check health
curl http://localhost:8000/api/v1/heartbeat
```

### Data Operations
```bash
# Always activate venv first!
source venv/bin/activate

# Re-ingest data after config changes
python ingest_data.py config.yaml

# Check version compatibility
python scripts/check_versions.py

# Collection management
python scripts/manage.py config.yaml
```

## Virtual Environment

**Critical:** Always activate the virtual environment before running Python scripts:

- **macOS/Linux**: `source venv/bin/activate`
- **Windows**: `venv\Scripts\activate`
- **Verify**: Look for `(venv)` in your prompt
- **Deactivate**: Use `deactivate` command

## Next Steps

1. **[Setup MCP Integration](MCP_INTEGRATION.md)** - Connect to Claude
2. **[Configure for your org](CONFIGURATION.md)** - Customize settings
3. **[Troubleshoot issues](TROUBLESHOOTING.md)** - Fix common problems