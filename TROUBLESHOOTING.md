# Troubleshooting Guide

## Common Issues

### Docker Problems

**ChromaDB won't start:**
```bash
# Test Docker setup
scripts/test_docker.sh

# Manual start
docker compose up -d

# Check health
curl http://localhost:8000/api/v1/heartbeat

# View logs
docker compose logs -f chromadb
```

**Port 8000 already in use:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

### Virtual Environment Issues

**"Command not found" errors:**
```bash
# Always activate venv first!
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
which python

# If venv doesn't exist, recreate:
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Memory Issues

**System running out of memory:**
- Close other applications during ingestion
- Reduce `batch_size` in config.yaml:
  ```yaml
  processing:
    batch_size: 25  # Default is 50
  ```
- System auto-cleans at 80% memory usage

### MCP Connection Problems

**Claude Desktop not connecting:**
```bash
# Check version compatibility
python scripts/check_versions.py

# Verify chroma-mcp is installed
which chroma-mcp

# Test ChromaDB connection
curl http://localhost:8000/api/v1/heartbeat
```

**Common MCP errors:**
- **"spawn python ENOENT"**: Use full path to chroma-mcp executable
- **"SSL record layer failure"**: Add `--ssl false` argument  
- **"404 Not Found"**: Version mismatch - update ChromaDB
- **"Collection not found"**: Check collection name matches exactly

### No Search Results

**Empty results from queries:**
```bash
# Check collection exists
python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
print(client.list_collections())
"

# Verify collection name format
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
org_name = config['organization']['name'].lower().replace(' ', '_').replace('-', '_')
base_name = config['chromadb']['collection_name']
print(f'Expected: {org_name}_{base_name}')
"

# Re-ingest data
source venv/bin/activate
python ingest_data.py config.yaml
```

### Installation Failures

**Requirements installation fails:**
```bash
# Clean install
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**PyTorch/M1 compatibility issues:**
```bash
# For Apple M1/M2 Macs
pip uninstall torch
pip install torch torchvision torchaudio
```

### Configuration Errors

**YAML parsing errors:**
```bash
# Validate YAML syntax
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
print('Config is valid!')
"
```

**Path not found errors:**
- Check that `data_sources.documentation.base_path` exists
- Use absolute paths, not relative paths
- Ensure you have read permissions

## Performance Issues

### Slow Ingestion

- Reduce `batch_size` in config.yaml
- Use SSD storage if possible
- Close other applications during ingestion
- Check available RAM

### Slow Queries

- Reduce `n_results` in queries
- Use more specific search terms
- Check ChromaDB container resources

## Getting Help

### Diagnostic Commands

```bash
# System info
scripts/test_docker.sh
python scripts/check_versions.py
python test_setup.py config.yaml

# Check logs
docker compose logs chromadb
tail -f *_ingestion.log
```

### Debug Information

When reporting issues, include:

1. **System info**: OS, Python version, Docker version
2. **Error message**: Full error output
3. **Configuration**: Your config.yaml (remove sensitive info)
4. **Versions**: Output of `python scripts/check_versions.py`
5. **Logs**: ChromaDB logs and ingestion logs

### Reset Everything

**Nuclear option - complete reset:**
```bash
# Stop everything
docker compose down

# Remove all data
rm -rf venv
docker volume prune -f

# Start fresh
./setup.sh config.yaml
```

## Known Issues

### Version Compatibility

- ChromaDB server 0.4.x with client 1.x causes API errors
- Solution: Use ChromaDB server 0.5.23+ with client 1.0.15+

### Platform Specific

**macOS Catalina+**: May need to allow Docker in Security settings
**Windows WSL**: Use Linux paths for documentation
**Linux**: Ensure Docker daemon is running

### Resource Limits

**Docker Desktop**: Increase memory allocation to 4GB+
**Low RAM systems**: Use batch_size: 10-25 in config