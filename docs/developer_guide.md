# Developer Guide

This guide is for developers who want to understand, modify, or contribute to the Universal Organization RAG System.

## 🏗 Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Universal RAG System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📄 Data Sources          🧠 Processing Pipeline               │
│  ┌─────────────────┐     ┌─────────────────────────────────┐   │
│  │ • Markdown Docs │────▶│ UniversalDocumentProcessor      │   │
│  │ • GitHub Issues │     │ • Content categorization       │   │
│  │ • Frontmatter   │     │ • Team mapping                 │   │
│  │ • Multiple dirs │     │ • Insight extraction           │   │
│  └─────────────────┘     │ • Chunking & tokenization      │   │
│                          └─────────────────────────────────┘   │
│                                           │                     │
│  ⚙️ Configuration                         ▼                     │
│  ┌─────────────────┐     ┌─────────────────────────────────┐   │
│  │ config.yaml     │────▶│ UniversalConfig                 │   │
│  │ • Organization  │     │ • Load & validate config       │   │
│  │ • Teams         │     │ • Provide access properties    │   │
│  │ • Goals         │     │ • Handle defaults              │   │
│  │ • Processing    │     └─────────────────────────────────┘   │
│  └─────────────────┘                      │                    │
│                                           ▼                     │
│  🔍 Vector Storage                ┌─────────────────────────────┐   │
│  ┌─────────────────┐             │ UniversalChromaDBIngester   │   │
│  │ ChromaDB        │◀────────────│ • Embedding generation      │   │
│  │ • Collections   │             │ • Batch processing          │   │
│  │ • Embeddings    │             │ • Memory monitoring         │   │
│  │ • Metadata      │             │ • Cross-platform device     │   │
│  │ • Filtering     │             └─────────────────────────────┘   │
│  └─────────────────┘                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Classes

#### 1. `UniversalConfig`
- **Purpose**: Load and validate YAML configuration
- **Key Methods**:
  - `__init__(config_path)`: Load config from file
  - Properties for accessing config sections
  - Collection name generation

#### 2. `UniversalDocumentProcessor`
- **Purpose**: Process markdown files and extract metadata
- **Key Methods**:
  - `process_markdown_file()`: Main processing pipeline
  - `determine_content_category()`: Categorize content
  - `enhance_metadata_with_teams()`: Add team mappings
  - `chunk_text()`: Split into searchable chunks

#### 3. `UniversalInsightExtractor`
- **Purpose**: Extract business insights from content
- **Key Methods**:
  - `extract_insights()`: Find pain points, value props, teams
  - `setup_keywords()`: Configure based on goals

#### 4. `UniversalChromaDBIngester`
- **Purpose**: Manage ChromaDB operations
- **Key Methods**:
  - `connect()`: Connect to ChromaDB
  - `load_embedding_model()`: Load sentence transformers
  - `ingest_batch()`: Process document batches

## 📁 File Structure

```
universal-org-rag/
├── 📋 README.md                    # Main documentation
├── ⚙️ config_template.yaml         # Configuration template
├── 🐳 docker-compose.yml           # ChromaDB container
├── 📦 requirements.txt             # Python dependencies
├── 🚀 setup.sh                     # Main setup script
├── 📊 ingest_data.py               # Data ingestion engine
├── 🧪 test_setup.py                # System testing
├── 🚫 .gitignore                   # Git ignore rules
│
├── 📁 config_examples/             # Example configurations
│   ├── startup_company.yaml
│   ├── tech_company.yaml
│   ├── consulting_firm.yaml
│   └── personal_knowledge.yaml
│
├── 📁 scripts/                     # Utility scripts
│   ├── test_docker.sh             # Docker compatibility test
│   ├── interview_prep.py          # Interview preparation tool
│   ├── manage.py                  # System management CLI
│   └── test_comprehensive.py      # Comprehensive test suite
│
└── 📁 docs/                       # Additional documentation
    ├── developer_guide.md         # This file
    ├── configuration_guide.md     # Configuration details
    └── deployment_guide.md        # Deployment instructions
```

## 🔧 Development Setup

### Prerequisites

```bash
# Required tools
brew install python3 docker
# OR
apt-get install python3 docker.io docker-compose

# Clone repository
git clone <repository-url>
cd universal-org-rag
```

### Development Environment

```bash
# Create development environment
python3 -m venv dev_venv
source dev_venv/bin/activate

# Install dependencies + dev tools
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
# Quick test suite
python test_setup.py

# Comprehensive test suite
python scripts/test_comprehensive.py

# With pytest for detailed output
python scripts/test_comprehensive.py --pytest

# Test specific functionality
python -m pytest scripts/test_comprehensive.py::TestConfiguration -v
```

## 🛠 Adding New Features

### Adding a New Data Source

1. **Extend Configuration Schema**
```yaml
# config_template.yaml
data_sources:
  new_source:
    enabled: false
    source_path: "/path/to/source"
    additional_config: "value"
```

2. **Add Config Properties**
```python
# ingest_data.py - UniversalConfig class
@property
def new_source_enabled(self) -> bool:
    return self.config['data_sources'].get('new_source', {}).get('enabled', False)

@property  
def new_source_path(self) -> Optional[str]:
    if self.new_source_enabled:
        return self.config['data_sources']['new_source'].get('source_path')
    return None
```

3. **Add Processing Logic**
```python
# ingest_data.py - UniversalDocumentProcessor class
def process_new_source_file(self, file_path: Path) -> List[Dict[str, Any]]:
    """Process files from new source"""
    try:
        # Your processing logic here
        # Return list of chunks with metadata
        pass
    except Exception as e:
        logging.error(f"Error processing new source file {file_path}: {e}")
        return []
```

4. **Integrate in Main Pipeline**
```python
# ingest_data.py - main() function
if config.new_source_enabled and config.new_source_path:
    logging.info("🔄 Processing new source...")
    source_files = list(get_new_source_files(config.new_source_path))
    
    for file_path in source_files:
        chunks = processor.process_new_source_file(file_path)
        batch_chunks.extend(chunks)
```

### Adding New Content Categories

1. **Update Configuration**
```yaml
# config_template.yaml
content_categories:
  new_category:
    keywords: ["keyword1", "keyword2", "specific_term"]
    importance: "high"  # high, medium, low
```

2. **Update Processing Logic**
```python
# ingest_data.py - UniversalDocumentProcessor.determine_content_category()
# The method automatically picks up new categories from config
# No code changes needed if using keyword matching

# For custom logic:
def determine_content_category(self, file_path: Path, content: str = "") -> str:
    # ... existing logic ...
    
    # Custom detection for new category
    if self.custom_new_category_detection(content):
        return "new_category"
    
    # ... rest of method ...
```

### Adding New Team Types

Teams are fully configurable via YAML - no code changes needed:

```yaml
target_teams:
  - name: "your_new_team"
    keywords: ["team_keyword", "department_name", "function"]
    aliases: ["alias1", "alias2"]
```

### Adding New Insight Extraction

1. **Extend Insight Extractor**
```python
# ingest_data.py - UniversalInsightExtractor class
def extract_insights(self, content: str, content_type: str) -> Dict[str, Any]:
    insights = {
        # ... existing insights ...
        "new_insight": self.detect_new_insight(content)
    }
    return insights

def detect_new_insight(self, content: str) -> bool:
    """Detect your new insight type"""
    # Your detection logic
    return False
```

2. **Update Tests**
```python
# scripts/test_comprehensive.py
def test_new_insight_extraction(self):
    """Test new insight extraction"""
    content = "Content that should trigger new insight"
    insights = self.insight_extractor.extract_insights(content, "test")
    assert "new_insight" in insights
```

## 🧪 Testing Guidelines

### Test Structure

```python
class TestNewFeature:
    """Test new feature functionality"""
    
    def setup_method(self):
        """Setup before each test"""
        self.config = create_test_config()
        
    def teardown_method(self):
        """Cleanup after each test"""
        # Clean up resources
        
    def test_feature_functionality(self):
        """Test the main functionality"""
        # Arrange
        # Act  
        # Assert
```

### Test Categories

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **Configuration Tests**: Test config validation
4. **End-to-End Tests**: Test complete workflows

### Adding Tests

```python
# scripts/test_comprehensive.py
def test_your_new_feature(self):
    """Test your new feature"""
    # Test setup
    test_data = "your test data"
    
    # Execute feature
    result = your_feature_function(test_data)
    
    # Verify results
    assert result is not None
    assert "expected_key" in result
    assert result["expected_key"] == "expected_value"
```

## 📊 Configuration System

### Configuration Hierarchy

1. **Template** (`config_template.yaml`): Documented template with all options
2. **Examples** (`config_examples/`): Real-world examples
3. **User Config** (`config.yaml`): User's actual configuration

### Adding Configuration Options

1. **Document in Template**
```yaml
# config_template.yaml
new_section:
  new_option: "default_value"  # REQUIRED: Description of what this does
  another_option: false        # OPTIONAL: Additional configuration
```

2. **Add to Example Configs**
```yaml
# config_examples/*.yaml
new_section:
  new_option: "example_value_for_this_org_type"
```

3. **Add Config Property**
```python
# ingest_data.py - UniversalConfig
@property
def new_option(self) -> str:
    return self.config['new_section']['new_option']
```

4. **Add Validation** (if needed)
```python
def validate_new_section(self):
    """Validate new configuration section"""
    if 'new_section' not in self.config:
        raise ValueError("new_section is required")
    # Additional validation
```

## 🔍 Debugging and Troubleshooting

### Logging

The system uses Python's logging module:

```python
import logging

# Log levels used:
logging.debug("Detailed debugging information")
logging.info("General information about processing")
logging.warning("Something unexpected but not fatal")
logging.error("Error that should be investigated")

# Configure logging level in config.yaml:
output:
  log_level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

### Common Issues

1. **Memory Issues**: Reduce `batch_size` in configuration
2. **Docker Issues**: Use `scripts/test_docker.sh` to diagnose
3. **Embedding Issues**: Check device compatibility (CPU/CUDA/MPS)
4. **Port Conflicts**: Change port in `docker-compose.yml`

### Debug Mode

```bash
# Enable debug logging
python ingest_data.py config.yaml --debug

# Run with memory monitoring
python -c "
import psutil
print(f'Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB')
"
```

## 🚀 Performance Optimization

### Memory Optimization

1. **Reduce batch size** for limited memory
2. **Use memory monitoring** to trigger cleanup
3. **Process priority paths first** for early feedback

### Speed Optimization

1. **Use faster embedding models** for development
2. **Increase batch size** for more memory
3. **Parallelize processing** (future enhancement)

### Storage Optimization

1. **Use exclude patterns** to skip unnecessary files
2. **Set minimum content length** to skip tiny files
3. **Regular cleanup** of old embeddings

## 🤝 Contributing Guidelines

### Code Style

```bash
# Format code with black
black ingest_data.py test_setup.py scripts/

# Check style with flake8  
flake8 ingest_data.py --max-line-length=100

# Type checking with mypy
mypy ingest_data.py --ignore-missing-imports
```

### Pull Request Process

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Add tests**: Ensure new functionality is tested
3. **Update documentation**: Update relevant docs
4. **Test thoroughly**: Run comprehensive test suite
5. **Submit PR**: With clear description of changes

### Commit Messages

```
feat: add support for Notion integration
fix: resolve memory leak in batch processing
docs: update configuration guide
test: add tests for team metadata extraction
refactor: simplify content categorization logic
```

## 📝 Documentation

### Updating Documentation

1. **README.md**: User-facing documentation
2. **docs/**: Detailed guides and references
3. **Code comments**: Inline documentation
4. **Configuration**: YAML comments and examples

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add troubleshooting sections
- Keep examples up-to-date

## 🔮 Future Enhancements

### Planned Features

1. **Additional Data Sources**
   - Notion integration
   - Confluence integration
   - Slack message processing
   - Google Docs integration

2. **Advanced Processing**
   - Parallel processing
   - Incremental updates
   - Content deduplication
   - Multi-language support

3. **Better Insights**
   - Sentiment analysis
   - Entity extraction
   - Relationship mapping
   - Trend analysis

4. **Enhanced Interfaces**
   - Web UI for configuration
   - API server mode
   - Slack bot integration
   - VS Code extension

### Architecture Improvements

1. **Plugin System**: Modular data source plugins
2. **Caching Layer**: Cache embeddings and processing results
3. **Monitoring**: Health checks and metrics
4. **Scaling**: Horizontal scaling support

---

**Happy coding! 🚀**

For questions or contributions, please refer to the main README.md or open an issue in the repository.
