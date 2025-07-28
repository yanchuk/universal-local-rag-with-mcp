# MCP Integration Guide

Connect your knowledge base to Claude Desktop and Claude Code CLI.

## Prerequisites

- Complete basic setup first (`./setup.sh`)
- ChromaDB running (`docker compose up -d`)
- Virtual environment activated (`source venv/bin/activate`)

## Claude Desktop (Automated)

**Recommended approach - fully automated:**

```bash
source venv/bin/activate
python scripts/setup_mcp.py
```

This script will:
- Find your collection name automatically
- Locate chroma-mcp executable
- Update Claude Desktop configuration
- Verify compatibility

**Then restart Claude Desktop and test with queries like:**
- "List available tools"
- "Search for company culture"
- "What are our team structures?"

## Claude Code CLI

### Method 1: Direct Command

```bash
# Get your chroma-mcp path
source venv/bin/activate
which chroma-mcp

# Add MCP server (replace paths with your actual paths)
claude mcp add your_org_knowledge -s user -- /path/to/venv/bin/chroma-mcp --client-type http --host localhost --port 8000 --ssl false

# Test
claude mcp list
claude "Search my organization knowledge for company values"
```

### Method 2: Import from Desktop

If you already configured Claude Desktop:

```bash
claude mcp import desktop
```

## Manual Configuration

### Find Your Collection Name

```bash
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
org_name = config['organization']['name'].lower().replace(' ', '_').replace('-', '_')
base_name = config['chromadb']['collection_name']
print(f'Collection: {org_name}_{base_name}')
"
```

### Claude Desktop Config File

**Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `~/AppData/Roaming/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "your_org_knowledge": {
      "command": "/full/path/to/venv/bin/chroma-mcp",
      "args": [
        "--client-type", "http",
        "--host", "localhost",
        "--port", "8000",
        "--ssl", "false"
      ]
    }
  }
}
```

## Verification

### Check ChromaDB
```bash
curl http://localhost:8000/api/v1/heartbeat
```

### Check Versions
```bash
source venv/bin/activate
python scripts/check_versions.py
```

### Test Queries
```python
import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection("your_collection_name")

results = collection.query(
    query_texts=["What are our company values?"],
    n_results=3
)
```

## Common Issues

- **Connection failed**: Check if ChromaDB is running
- **Collection not found**: Verify collection name matches exactly
- **SSL errors**: Ensure `--ssl false` is included
- **Version conflicts**: Run `python scripts/check_versions.py`

See [Troubleshooting Guide](TROUBLESHOOTING.md) for detailed fixes.