# 🚀 Universal Local RAG with MCP

A configurable Retrieval-Augmented Generation (RAG) system for building searchable knowledge bases from your organization's documentation, GitHub issues, and other content sources. Designed to work locally with Claude MCP integration for powerful, private knowledge management.

**🔗 Repository**: https://github.com/yanchuk/universal-local-rag-with-mcp

## 🎓 Educational Project

**Built for educational purposes** during a weekend learning session with **Claude Sonnet 4**. This project demonstrates how to build a universal, configurable RAG system that works with any organization's documentation without requiring custom development.

**Tested extensively on Apple M1/M2 hardware** with cross-platform compatibility for Intel systems and Linux.

**Learning Objectives:**
- Universal system design and configuration management
- RAG implementation with ChromaDB and sentence transformers  
- Cross-platform compatibility and Docker deployment
- Production-ready software engineering practices

## ✨ Features

- **🏢 Universal Configuration**: Works with any organization's documentation structure
- **📚 Multi-Source Ingestion**: Markdown docs, GitHub issues, team documentation
- **🎯 Goal-Oriented**: Configurable for interview prep, onboarding, knowledge management
- **⚙️ Team-Aware**: Automatically maps content to teams and departments
- **🔍 Smart Categorization**: AI-powered content classification and metadata enhancement
- **💻 Cross-Platform**: Optimized for M1/M2 Macs, Intel systems, and Linux
- **🐳 Containerized**: ChromaDB runs in Docker for easy setup and portability

## 🎯 Use Cases

### Interview Preparation
- Research company culture, values, and decision-making processes
- Understand team dynamics and responsibilities  
- Learn customer problems and product strategy
- Practice with organization-specific knowledge

### Knowledge Management
- Searchable company documentation
- Team onboarding and training
- Cross-team collaboration insights
- Customer insight analysis

### Onboarding Support
- New hire orientation materials
- Department-specific knowledge paths
- Culture and process understanding
- Mentor conversation starters

## 🚀 Quick Start

### TL;DR - 3 Steps to Get Running
```bash
# 1. Clone and setup
git clone https://github.com/yanchuk/universal-local-rag-with-mcp.git
cd universal-local-rag-with-mcp
cp config_examples/startup_company.yaml config.yaml
# Edit config.yaml with your organization details
./setup.sh

# 2. Setup Claude Desktop MCP (automated)
source venv/bin/activate
python scripts/setup_mcp.py

# 3. Setup Claude Code CLI MCP (see below)
```

### Prerequisites
- **Docker Desktop** (for ChromaDB) - must be running
- **Python 3.8+**
- **4GB+ RAM** (8GB recommended, tested on Apple M1/M2)
- **2GB disk space** for embeddings and data
- **No pip installs needed** - setup script handles everything automatically

### 1. Setup
```bash
git clone https://github.com/yanchuk/universal-local-rag-with-mcp.git
cd universal-local-rag-with-mcp

# Choose or create your configuration
cp config_examples/startup_company.yaml config.yaml
# Edit config.yaml with your organization details

# Run setup (auto-detects docker-compose vs docker compose)
# You might need to provide permissions with `chmod +x setup.sh`
./setup.sh
```

### 2. Configure
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
  focus_areas:
    - "company_culture"
    - "team_dynamics"
    - "customer_insights"
```

### 3. Test Your Setup

**🚨 Important: Always activate the virtual environment first!**

```bash
# STEP 1: Activate the virtual environment created by setup.sh
source venv/bin/activate

# For Windows users:
# venv\Scripts\activate

# STEP 2: Run comprehensive tests with your config
python test_setup.py config.yaml

# STEP 3: Optional tests
./scripts/test_docker.sh                    # Test Docker compatibility
python scripts/interview_prep.py config.yaml  # Interactive interview preparation
```

**Virtual Environment Notes:**
- **macOS/Linux**: `source venv/bin/activate`
- **Windows**: `venv\Scripts\activate`
- **Check activation**: Your prompt should show `(venv)` prefix
- **Deactivate**: Use `deactivate` command when done
- **Why needed**: Isolates Python dependencies from system Python

## 🔧 Claude MCP Integration

**📋 Prerequisites:**
- **Complete the basic setup first** (run `./setup.sh` successfully)
- ChromaDB running locally (`docker compose up -d`)
- Claude Desktop app installed
- **IMPORTANT**: Virtual environment activated (`source venv/bin/activate`)

**🔧 Step 1: Verify MCP Installation**
```bash
# Activate virtual environment first!
source venv/bin/activate

# Verify chroma-mcp is installed (should be installed by setup.sh)
which chroma-mcp
# If not found, install it: pip install chroma-mcp
```

**🔧 Step 2: Find Your Collection Name**
```bash
# Your collection name format: {organization_name}_{collection_name}
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
org_name = config['organization']['name'].lower().replace(' ', '_').replace('-', '_')
base_name = config['chromadb']['collection_name']
print(f'Collection name: {org_name}_{base_name}')
"
```

**🔧 Step 3: Create Claude MCP Configuration**

Update `claude_desktop_config.json` (find config file at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

#### **Correct Configuration:**
```json
{
  "mcpServers": {
    "your_org_knowledge": {
      "command": "/full/path/to/your/venv/bin/chroma-mcp",
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

**🔧 Step 4: Get Your Exact Paths**
```bash
# Get your venv path
source venv/bin/activate
which chroma-mcp

# This will output something like:
# /Users/yourname/git/universal-local-rag-with-mcp/venv/bin/chroma-mcp
```

**🔧 Step 5: Update Configuration with Your Paths**

Replace the `command` field with your actual path from Step 4:
```json
{
  "mcpServers": {
    "your_org_knowledge": {
      "command": "/Users/yourname/git/universal-local-rag-with-mcp/venv/bin/chroma-mcp",
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

**🔧 Step 6: Restart Claude Desktop and Test**

1. **Save the configuration file**
2. **Restart Claude Desktop completely**
3. **Test with queries like:**
   ```
   List available tools
   Search for company culture
   What are our team structures?
   ```

**🚀 Alternative: Automated Setup**
```bash
# Skip manual configuration - use the automated script instead!
source venv/bin/activate
python scripts/setup_mcp.py
# This will automatically configure Claude Desktop for you
```

**🚨 Troubleshooting MCP Connection:**
- **"spawn python ENOENT"**: Use full path to `chroma-mcp` executable in virtual environment
- **"SSL record layer failure"**: Add `--ssl false` argument for local HTTP connections
- **"404 Not Found" or API version errors**: Ensure ChromaDB server version matches client (both should be compatible)
- **"Connection failed"**: Check if ChromaDB is running (`curl http://localhost:8000/api/v1/heartbeat`)
- **"Collection not found"**: Verify collection name matches exactly
- **JSON parsing errors**: Check Claude Desktop logs for malformed JSON in config file

## 🖥️ Claude Code CLI Integration

**For Claude Code CLI users, there's a simpler approach using the `claude mcp add` command:**

**📋 Prerequisites:**
- **Complete the basic setup first** (run `./setup.sh` successfully)
- ChromaDB running locally and knowledge base ingested
- Claude Code CLI installed and working

**🔧 Step 1: Get Your Paths**
```bash
# Activate virtual environment and get the chroma-mcp path
source venv/bin/activate
which chroma-mcp
# Example output: /Users/yourname/git/universal-local-rag-with-mcp/venv/bin/chroma-mcp
```

**🔧 Step 2: Add MCP Server to Claude Code CLI**
```bash
# Add your knowledge base as an MCP server
claude mcp add your_org_knowledge -s user -- /Users/yourname/git/universal-local-rag-with-mcp/venv/bin/chroma-mcp --client-type http --host localhost --port 8000 --ssl false

# Replace "your_org_knowledge" with your organization name
# Replace the path with your actual chroma-mcp path from Step 1
```

**🔧 Step 3: Test the Connection**
```bash
# List available MCP servers
claude mcp list

# Test with queries
claude "Search my organization knowledge for company values"
```

**🔧 Alternative: Import from Claude Desktop Configuration**

If you already have Claude Desktop configured (using `scripts/setup_mcp.py`):

```bash
# Copy your Claude Desktop MCP config to Claude Code CLI
claude mcp import desktop
```

### 4. Query Your Knowledge Base (Python API)
```python
import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection("yourcompany_organization_knowledge")

results = collection.query(
    query_texts=["What are our company values?"],
    n_results=3
)

for doc in results['documents'][0]:
    print(doc[:200] + "...")
```

## 📋 Configuration Examples

### 🤖 Configuration Logic

The system uses YAML configuration files to adapt to any organization. The key is defining:

1. **Organization details** (name, description, domain)
2. **RAG goals** (interview prep, knowledge management, onboarding)
3. **Target teams** with relevant keywords for content mapping
4. **Data sources** (documentation paths, GitHub issues)
5. **Processing settings** optimized for your hardware and scale

### 🎆 AI-Generated Configurations (Recommended)

Use this prompt with any LLM (Claude, ChatGPT, etc.) to generate production-ready configs:

```
I need to create a configuration file for a Universal Organization RAG System. 

Please generate a config.yaml file for:

ORGANIZATION: [Your company name]
TYPE: [startup/enterprise/consulting/personal]
PURPOSE: [interview_preparation/knowledge_management/onboarding]
TEAMS: [List the main teams/departments]
DOCS LOCATION: [Path to your documentation]
SPECIAL FOCUS: [Any specific areas to emphasize]

[Include complete template request...]
```

**Benefits**: Saves 30+ minutes, reduces errors, includes best practices automatically.

### 🏢 Example: Startup Company
```yaml
organization:
  name: "Acme Startup"
  description: "Fast-moving startup building the future of SaaS"

rag_goals:
  primary_purpose: "interview_preparation"
  focus_areas: ["company_culture", "product_strategy", "team_dynamics"]

target_teams:
  - name: "product"
    keywords: ["product", "pm", "roadmap", "features"]
  - name: "engineering"  
    keywords: ["engineering", "development", "technical"]
  - name: "growth"
    keywords: ["growth", "marketing", "acquisition"]

data_sources:
  documentation:
    base_path: "/path/to/your/docs"
    priority_paths: ["handbook", "product", "culture"]
```

**See `config_examples/` for complete configurations for startups, enterprises, consulting firms, and personal knowledge bases.**

## 🏗 Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   Data Sources      │    │   Processing         │    │   Vector Store  │
│                     │    │                      │    │                 │
│ 📄 Markdown Docs    │────│ 🧠 Content Analysis  │────│ 🗄️ ChromaDB     │
│ 🐛 GitHub Issues    │────│ ⚙️ Team Mapping      │────│   (Docker)      │
│ 👥 Team Docs        │────│ 🏢 Culture Extract   │────│                 │
│ 📊 Customer Stories │────│ 🎯 Goal Alignment    │────│ 🔍 Embeddings   │
└─────────────────────┘    └──────────────────────┘    └─────────────────┘
                                      │
                          ┌───────────▼──────────────┐
                          │   Enhanced Metadata      │
                          │ • content_category       │
                          │ • team_ownership         │
                          │ • is_goal_relevant       │
                          │ • has_pain_points        │
                          │ • customer_context       │
                          └──────────────────────────┘
```

## 📊 Content Categories

The system automatically classifies content into:

- **Company Culture** - Values, mission, decision-making processes
- **Team Documentation** - Responsibilities, processes, objectives  
- **Customer Stories** - Use cases, implementations, success stories
- **Product Strategy** - Roadmap, priorities, competitive positioning
- **Technical Docs** - APIs, implementation guides, architecture
- **General Docs** - Other documentation and resources

## 🔍 Query Patterns

### Company Culture
```python
results = collection.query(
    query_texts=["What are our company values and culture?"],
    where={"content_category": "company_culture"},
    n_results=5
)
```

### Team Insights
```python
results = collection.query(
    query_texts=["How does the engineering team work?"],
    where={"relates_to_engineering": True},
    n_results=5
)
```

### Customer Problems
```python
results = collection.query(
    query_texts=["What problems do our customers face?"],
    where={"has_pain_points": True},
    n_results=5
)
```

### Goal-Relevant Content
```python
results = collection.query(
    query_texts=["Important information for interview preparation"],
    where={"is_goal_relevant": True},
    n_results=10
)
```

## 🧪 Testing

### Basic Functionality
```bash
python test_setup.py config.yaml
```

### Docker Compatibility
```bash
scripts/test_docker.sh
```

### Interview Preparation
```bash
python scripts/interview_prep.py config.yaml
```

## 🛠 Management Commands

### Start/Stop ChromaDB
```bash
# Auto-detects docker-compose vs docker compose
docker compose up -d          # Start
docker compose down           # Stop
docker compose logs -f        # View logs
```

**Note**: The system uses ChromaDB v0.5.23 in Docker for compatibility with the MCP client v1.0.15. If you encounter version compatibility issues, ensure both client and server versions are compatible.

### Re-ingest Data
```bash
# IMPORTANT: Always activate virtual environment first
source venv/bin/activate
python ingest_data.py config.yaml
```

### Update Configuration
1. Edit `config.yaml`
2. Re-run `./setup.sh` or just the ingestion:
   ```bash
   # IMPORTANT: Always activate virtual environment first
   source venv/bin/activate
   python ingest_data.py config.yaml
   ```

## 📈 Performance

- **Setup Time**: 15-45 minutes (depending on documentation size)
- **Query Speed**: <500ms for most queries
- **Memory Usage**: 2-4GB during ingestion, <1GB during operation
- **Storage**: ~2GB for embeddings and database

## 🚨 Troubleshooting

### Docker Issues
```bash
# Test Docker setup
scripts/test_docker.sh

# Manual ChromaDB start
docker compose up -d
curl http://localhost:8000/api/v1/heartbeat
```

### Memory Issues
- Close other applications during ingestion
- Reduce `batch_size` in config.yaml
- System will auto-cleanup at 80% memory usage

### No Results Found
- Check collection name: `{org_name}_{collection_name}`
- Verify configuration paths exist
- Re-run ingestion if data changed

### PyTorch/M1 Issues
```bash
# Clean install
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🤝 Contributing

1. **Add new content sources**: Extend `UniversalDocumentProcessor`
2. **Improve categorization**: Update content classification logic
3. **Add integrations**: Create new MCP connectors or API wrappers
4. **Optimize performance**: Improve embedding generation or query speed

## 📄 License

MIT License - feel free to adapt for your organization's needs.

## 🎯 Examples

See `config_examples/` for ready-to-use configurations:
- `startup_company.yaml` - Early-stage startup
- `tech_company.yaml` - Established tech company  
- `consulting_firm.yaml` - Professional services
- `personal_knowledge.yaml` - Personal documentation

## 💡 Tips

### For Interview Preparation
1. Focus on `company_culture` and `team_documentation` content
2. Practice with goal-relevant queries
3. Understand team structures and responsibilities
4. Research customer problems and solutions

### For Knowledge Management
1. Set up regular re-ingestion schedules
2. Create team-specific query templates
3. Train users on effective search patterns
4. Monitor and update configurations as org evolves

### For Onboarding
1. Create progressive complexity paths
2. Build team-specific question guides  
3. Develop culture exploration workflows
4. Set up mentor conversation starters

---

**🚀 Transform your organization's documentation into a powerful, searchable knowledge base!**
