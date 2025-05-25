# Quick Start Guide

Get your Universal Organization RAG system running in under 30 minutes.

## ⚡ 5-Minute Setup

### Prerequisites Check

```bash
# Verify you have the essentials
docker --version    # Should show Docker version
python3 --version   # Should show Python 3.8+
```

### Download and Configure

```bash
# Clone the repository
git clone <your-repository-url>
cd universal-org-rag

# Choose your configuration template
cp config_examples/startup_company.yaml config.yaml
```

### Essential Configuration

Edit `config.yaml` - only change these 3 lines:

```yaml
organization:
  name: "YourCompany"  # ← Change this to your company name

data_sources:
  documentation:
    base_path: "/path/to/your/docs"  # ← Point to your documentation folder

rag_goals:
  primary_purpose: "interview_preparation"  # ← Choose: interview_preparation, knowledge_management, or onboarding
```

### Launch

```bash
# Test Docker compatibility (optional but recommended)
chmod +x scripts/test_docker.sh
./scripts/test_docker.sh

# Run the complete setup
chmod +x setup.sh
./setup.sh
```

**That's it!** Your RAG system is now running.

## 🧪 Test Your System

```bash
# Quick test
python test_setup.py

# Interactive interview preparation
python scripts/interview_prep.py
```

## 🔍 Query Your Knowledge

```python
import chromadb

# Connect to your knowledge base
client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection("yourcompany_organization_knowledge")

# Search your documentation
results = collection.query(
    query_texts=["What are our company values?"],
    n_results=3
)

for doc in results['documents'][0]:
    print(doc[:200] + "...")
```

## 🎯 What You Get

- **🔍 Searchable Knowledge**: All your docs in one searchable database
- **🎤 Interview Prep**: AI-powered interview question practice
- **⚙️ Team Insights**: Understanding of team structures and responsibilities
- **🏢 Culture Analysis**: Deep insights into company culture and values
- **📊 Customer Intelligence**: Analysis of customer problems and solutions

## 📋 Configuration Templates

| Template | Best For | Focus |
|----------|----------|-------|
| `startup_company.yaml` | Early-stage startups | Culture, product vision, rapid growth |
| `tech_company.yaml` | Established tech companies | Technical architecture, multiple teams |
| `consulting_firm.yaml` | Professional services | Methodologies, client work, expertise |
| `personal_knowledge.yaml` | Individual use | Personal notes, research, projects |

## 🚀 Advanced Setup (Optional)

### Custom Team Configuration

```yaml
target_teams:
  - name: "your_team"
    keywords: ["team", "department", "function"]
    aliases: ["alt-name", "abbreviation"]
```

### GitHub Integration

```yaml
data_sources:
  github:
    enabled: true
    issues_path: "/path/to/github/issues"
```

### Performance Tuning

```yaml
processing:
  batch_size: 32        # 16 for low memory, 64 for high performance
  max_chunk_size: 1200  # 800 for speed, 1500 for quality
```

## 🛠 Management Commands

```bash
# System status
python scripts/manage.py status

# Start/stop ChromaDB
python scripts/manage.py start
python scripts/manage.py stop

# Re-ingest data after changes
python scripts/manage.py ingest

# Create backup
python scripts/manage.py backup
```

## 🔧 Integration

### Claude MCP Setup

Create `claude_mcp_config.json`:

```json
{
  "mcpServers": {
    "org_knowledge": {
      "command": "python",
      "args": ["-m", "chromadb.mcp"],
      "env": {
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": "8000",
        "CHROMA_COLLECTION": "yourcompany_organization_knowledge"
      }
    }
  }
}
```

### Python API Usage

```python
class OrganizationKnowledge:
    def __init__(self):
        self.client = chromadb.HttpClient(host="localhost", port=8000)
        self.collection = self.client.get_collection("yourcompany_organization_knowledge")
    
    def search_culture(self, query="company values"):
        return self.collection.query(
            query_texts=[query],
            where={"content_category": "company_culture"},
            n_results=5
        )
    
    def search_teams(self, team_name):
        return self.collection.query(
            query_texts=[f"{team_name} team responsibilities"],
            where={f"relates_to_{team_name}": True},
            n_results=3
        )
```

## 🚨 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| `docker-compose: command not found` | Script auto-detects this - just run `./setup.sh` |
| Port 8000 in use | Change port in `docker-compose.yml` |
| Memory issues | Reduce `batch_size` in `config.yaml` |
| No results found | Check collection name matches your org |
| Docker won't start | Run `scripts/test_docker.sh` to diagnose |

## 💡 Pro Tips

1. **Start Small**: Begin with one documentation folder, expand gradually
2. **Use Priority Paths**: Put most important docs in `priority_paths`
3. **Regular Updates**: Re-run ingestion when docs change
4. **Explore Categories**: Check what content categories were detected
5. **Practice Queries**: Use different search terms to find the best results

## 📖 Next Steps

- **Explore**: Try different search queries to understand your data
- **Customize**: Adjust team and category configurations
- **Integrate**: Connect with Claude or other AI tools
- **Scale**: Add more documentation sources
- **Share**: Set up for team-wide access

## 🆘 Need Help?

- **Configuration Issues**: See [Configuration Guide](docs/configuration_guide.md)
- **Technical Problems**: See [Developer Guide](docs/developer_guide.md)
- **Deployment**: See [Deployment Guide](docs/deployment_guide.md)
- **General Usage**: See main [README](README.md)

---

**🎉 Welcome to your new superpower: instant access to all your organization's knowledge!**
