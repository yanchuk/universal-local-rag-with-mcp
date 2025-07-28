# Configuration Guide

## Quick Setup

Use these templates from `config_examples/`:

```bash
# Startup company
cp config_examples/startup_company.yaml config.yaml

# Tech company  
cp config_examples/tech_company.yaml config.yaml

# Personal knowledge base
cp config_examples/personal_knowledge.yaml config.yaml
```

## Configuration Structure

```yaml
organization:
  name: "YourCompany"
  description: "Brief description"
  domain: "yourcompany.com"

rag_goals:
  primary_purpose: "interview_preparation"  # or "knowledge_management", "onboarding"
  focus_areas:
    - "company_culture"
    - "team_dynamics" 
    - "customer_insights"

target_teams:
  - name: "engineering"
    keywords: ["engineering", "development", "technical", "backend", "frontend"]
  - name: "product"
    keywords: ["product", "pm", "roadmap", "features", "user"]

data_sources:
  documentation:
    base_path: "/path/to/your/docs"
    priority_paths:
      - "handbook"
      - "culture"
      - "processes"
  
  github:
    enabled: false
    # owner: "your-org"
    # repos: ["main-repo"]

chromadb:
  collection_name: "organization_knowledge"
  
processing:
  batch_size: 50
  chunk_size: 1000
  chunk_overlap: 200
```

## Examples by Use Case

### Interview Preparation

Focus on culture, processes, and team dynamics:

```yaml
rag_goals:
  primary_purpose: "interview_preparation"
  focus_areas:
    - "company_culture"
    - "team_dynamics"
    - "decision_making"
    - "customer_insights"

target_teams:
  - name: "engineering"
    keywords: ["engineering", "development", "technical"]
  - name: "product"
    keywords: ["product", "pm", "strategy"]
  - name: "design"
    keywords: ["design", "ux", "ui", "user"]
```

### Knowledge Management

Broader coverage for searchable docs:

```yaml
rag_goals:
  primary_purpose: "knowledge_management"
  focus_areas:
    - "processes"
    - "documentation"
    - "best_practices"
    - "technical_guides"

data_sources:
  documentation:
    base_path: "/company/docs"
    priority_paths:
      - "handbook"
      - "engineering"
      - "product"
      - "support"
```

### Onboarding

New hire orientation focus:

```yaml
rag_goals:
  primary_purpose: "onboarding"
  focus_areas:
    - "company_culture"
    - "processes"
    - "team_introductions"
    - "getting_started"

target_teams:
  - name: "all_teams"
    keywords: ["team", "department", "role", "responsibility"]
```

## Advanced Configuration

### Content Categories

The system automatically categorizes content:

- **company_culture** - Values, mission, decision-making
- **team_documentation** - Processes, responsibilities
- **customer_stories** - Use cases, success stories
- **product_strategy** - Roadmap, positioning
- **technical_docs** - APIs, architecture
- **general_docs** - Other documentation

### Processing Options

```yaml
processing:
  batch_size: 25           # Reduce for low memory
  chunk_size: 800          # Smaller chunks for detailed search
  chunk_overlap: 150       # Overlap between chunks
  min_content_length: 50   # Skip very short content
  
performance:
  memory_threshold: 0.8    # Auto-cleanup at 80% memory
  parallel_processing: true
```

### Team Mapping

Keywords help categorize content by team:

```yaml
target_teams:
  - name: "engineering"
    keywords: 
      - "engineering"
      - "development"
      - "technical"
      - "backend"
      - "frontend"
      - "api"
      - "database"
  
  - name: "product"
    keywords:
      - "product"
      - "pm"
      - "roadmap"
      - "features"
      - "user"
      - "customer"
```

## AI-Generated Configs

Use this prompt with any LLM to generate configs:

```
Generate a config.yaml for Universal Organization RAG System:

ORGANIZATION: [Your company name]
TYPE: [startup/enterprise/consulting/personal]  
PURPOSE: [interview_preparation/knowledge_management/onboarding]
TEAMS: [List main teams/departments]
DOCS PATH: [Path to documentation]
FOCUS: [Specific areas to emphasize]

Include complete YAML structure with organization details, RAG goals, target teams with keywords, data sources, and processing settings.
```

## Collection Naming

Your collection name will be: `{org_name}_{collection_name}`

Example:
- Organization: "Acme Startup" 
- Collection: "organization_knowledge"
- Result: `acme_startup_organization_knowledge`

Check your collection name:
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