# Universal Local RAG with MCP

A configurable RAG system for building searchable knowledge bases from your organization's documentation. Works locally with Claude MCP integration.

## Quick Start

```bash
# 1. Setup
git clone https://github.com/yanchuk/universal-local-rag-with-mcp.git
cd universal-local-rag-with-mcp
cp config_examples/startup_company.yaml config.yaml
./setup.sh

# 2. Test
source venv/bin/activate
python test_setup.py config.yaml

# 3. Setup Claude integration
python scripts/setup_mcp.py
```

## What It Does

- **📚 Ingests** Markdown docs, GitHub issues, team documentation
- **🔍 Searches** with AI-powered semantic search
- **🤖 Integrates** with Claude Desktop and Claude Code CLI
- **⚙️ Configures** for any organization via YAML

## Use Cases

- **Interview Preparation** - Research company culture and processes
- **Knowledge Management** - Searchable company documentation  
- **Onboarding** - New hire orientation and training

## Requirements

- Docker Desktop (for ChromaDB)
- Python 3.8+
- 4GB+ RAM

## Documentation

- **[Setup Guide](SETUP.md)** - Detailed installation instructions
- **[MCP Integration](MCP_INTEGRATION.md)** - Claude Desktop/CLI setup
- **[Configuration](CONFIGURATION.md)** - YAML config examples
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and fixes

## Architecture

```
Data Sources → Processing → ChromaDB → Claude MCP
📄 Docs      🧠 Analysis   🗄️ Vectors   🤖 Chat
```

## License

MIT - Feel free to adapt for your organization's needs.