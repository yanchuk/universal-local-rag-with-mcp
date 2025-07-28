# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Universal Local RAG with MCP is a configurable Retrieval-Augmented Generation (RAG) system designed to build searchable knowledge bases from organizational documentation, GitHub issues, and other content sources. It works locally with Claude MCP integration for private knowledge management.

Key characteristics:
- Educational project built for learning RAG implementation
- Universal configuration system that adapts to any organization
- Cross-platform compatibility (optimized for Apple M1/M2, Intel, Linux)
- Docker-based ChromaDB for vector storage
- Designed for interview preparation, knowledge management, and onboarding

## Architecture

The system follows a three-layer architecture:

1. **Data Sources Layer**: Ingests from Markdown docs, GitHub issues, team documentation
2. **Processing Layer**: Content analysis, team mapping, culture extraction, goal alignment
3. **Vector Store Layer**: ChromaDB with embeddings and enhanced metadata

Core components:
- `ingest_data.py`: Main ingestion script with UniversalDocumentProcessor
- `config.yaml`: YAML-based configuration for any organization 
- `setup.sh`: Cross-platform setup script with Docker auto-detection
- `test_setup.py`: Comprehensive testing suite
- `scripts/`: Management utilities (interview_prep.py, manage.py)

## Common Development Commands

### Environment Setup
```bash
# Initial setup (auto-detects docker-compose vs docker compose)
./setup.sh [config_file]

# Activate virtual environment (CRITICAL - always do this first)
source venv/bin/activate

# Windows users:
# venv\Scripts\activate
```

### ChromaDB Management
```bash
# Start ChromaDB container
docker compose up -d
# or
docker-compose up -d

# Stop ChromaDB
docker compose down

# View logs
docker compose logs -f chromadb

# Check health
curl http://localhost:8000/api/v1/heartbeat
```

### Data Ingestion
```bash
# Full ingestion with config validation
python ingest_data.py config.yaml

# Re-ingest after config changes
python ingest_data.py config.yaml
```

### Testing
```bash
# Comprehensive test suite (requires active venv)
python test_setup.py config.yaml

# Docker compatibility test
scripts/test_docker.sh

# Interview preparation interactive test
python scripts/interview_prep.py config.yaml
```

### Management Operations
```bash
# Collection statistics and management
python scripts/manage.py config.yaml

# Query collection name format
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
org_name = config['organization']['name'].lower().replace(' ', '_').replace('-', '_')
base_name = config['chromadb']['collection_name']
print(f'Collection: {org_name}_{base_name}')
"
```

## Configuration System

The system uses YAML configuration files (`config.yaml`) that define:
- Organization details (name, description, domain)
- RAG goals (interview_preparation, knowledge_management, onboarding)
- Target teams with keywords for content mapping
- Data sources (documentation paths, GitHub issues)
- Processing settings optimized for hardware

Example configurations are in `config_examples/`:
- `startup_company.yaml`
- `tech_company.yaml` 
- `consulting_firm.yaml`
- `personal_knowledge.yaml`

## Key Classes and Functions

### UniversalConfig (`ingest_data.py:37`)
Central configuration management class that loads YAML config and provides properties for:
- `organization_name`, `collection_name`
- `docs_path`, `github_enabled`, `target_teams`
- `rag_goals`, `processing_config`, `content_categories`

### UniversalDocumentProcessor (`ingest_data.py`)
Main document processing class with configurable:
- Content categorization (company_culture, product_strategy, team_documentation)
- Team mapping based on keywords
- Goal-relevant content detection
- Customer context and pain point extraction

### RAGManager (`scripts/manage.py:16`)
Management utilities for collection operations, statistics, and maintenance.

## Claude MCP Integration

The system integrates with Claude Desktop via MCP servers:

1. Collection name format: `{org_name}_{collection_name}`
2. ChromaDB runs on localhost:8000
3. Configure `claude_desktop_config.json` with collection name
4. Test with organization-specific queries

## Virtual Environment Requirements

**CRITICAL**: Always activate the virtual environment before running any Python scripts:
- macOS/Linux: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`
- Verify activation by checking for `(venv)` prefix in prompt

The project isolates dependencies to avoid conflicts with system Python.

## Memory and Performance

- Optimized for Apple M1/M2 hardware
- Memory usage monitoring with auto-cleanup at 80% threshold
- Configurable batch sizes and chunk parameters
- Cross-platform PyTorch compatibility

## Development Notes

- No package.json - this is a Python project
- Dependencies managed via requirements.txt with version pinning
- Docker auto-detection for compose vs docker-compose commands
- Comprehensive logging to `{purpose}_ingestion.log`
- Quality control with minimum content length and validation

## Troubleshooting Commands

```bash
# Docker issues
scripts/test_docker.sh
curl http://localhost:8000/api/v1/heartbeat

# Memory issues - reduce batch_size in config.yaml
# PyTorch/M1 issues - clean reinstall:
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# No results - verify collection name and re-ingest
python ingest_data.py config.yaml
```