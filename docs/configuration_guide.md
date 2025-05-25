# Configuration Guide

This guide helps you configure the Universal Organization RAG System for your specific needs.

## 🎯 Quick Configuration

### Step 1: Choose Your Template

```bash
# Copy the appropriate template
cp config_examples/startup_company.yaml config.yaml
# OR
cp config_examples/tech_company.yaml config.yaml  
# OR
cp config_examples/consulting_firm.yaml config.yaml
# OR
cp config_examples/personal_knowledge.yaml config.yaml
```

### Step 2: Basic Customization

Edit the essential fields in `config.yaml`:

```yaml
organization:
  name: "YourCompany"  # Replace with your actual organization name

data_sources:
  documentation:
    base_path: "/path/to/your/docs"  # Point to your documentation

rag_goals:
  primary_purpose: "interview_preparation"  # Choose your goal
  focus_areas:
    - "company_culture"     # Customize your focus areas
    - "team_dynamics"
```

### Step 3: Test Configuration

```bash
# Validate your configuration
python test_setup.py config.yaml

# If validation passes, run setup
./setup.sh config.yaml
```

## 📋 Complete Configuration Reference

### Organization Details

```yaml
organization:
  name: "YourCompany"              # REQUIRED: Your organization name
  description: "Brief description"  # Used in collection metadata
  domain: "company.com"            # Used for identification
```

**Guidelines:**
- Use your actual organization name for `name`
- Keep `description` brief but descriptive
- `domain` helps identify the organization in multi-tenant setups

### RAG Goals Configuration

```yaml
rag_goals:
  primary_purpose: "purpose"       # REQUIRED: Main use case
  focus_areas: []                  # REQUIRED: Areas of focus
  target_role: "role"              # OPTIONAL: Specific role optimization
```

#### Primary Purpose Options

| Purpose | Description | Best For |
|---------|-------------|----------|
| `interview_preparation` | Optimize for job interview prep | Job candidates researching companies |
| `knowledge_management` | General organizational knowledge | Teams needing searchable documentation |
| `onboarding` | New hire orientation | HR and onboarding programs |

#### Focus Areas Options

| Focus Area | Description | Useful For |
|------------|-------------|------------|
| `company_culture` | Values, mission, working style | Understanding organizational fit |
| `team_dynamics` | Team structure, collaboration | Understanding how teams work |
| `customer_insights` | Customer problems, use cases | Product and customer-facing roles |
| `product_strategy` | Roadmap, competitive positioning | Product management roles |
| `technical_architecture` | System design, tech stack | Engineering roles |
| `security_compliance` | Security practices, compliance | Security and compliance roles |

#### Target Role Options

| Role | Optimization | Focus |
|------|-------------|-------|
| `product_manager` | Product strategy, customer insights | PM-specific questions and insights |
| `engineer` | Technical architecture, processes | Engineering practices and tech stack |
| `designer` | User experience, design process | Design methodology and user research |
| `sales` | Customer problems, value props | Sales enablement and customer stories |
| `marketing` | Brand, messaging, growth | Marketing strategies and campaigns |
| `consultant` | Methodology, client insights | Consulting approaches and case studies |
| `general` | Balanced coverage | No specific role optimization |

### Data Sources Configuration

#### Documentation Sources

```yaml
data_sources:
  documentation:
    base_path: "/path/to/docs"     # REQUIRED: Root documentation path
    priority_paths:                # OPTIONAL: Process these first
      - "handbook"
      - "teams"
      - "customers"
    file_extensions:               # OPTIONAL: File types to process
      - "*.md"
      - "*.mdx"
      - "*.txt"
```

**Priority Paths Guidelines:**
- List most important directories first
- Common high-value paths:
  - `handbook` - Company handbook
  - `teams` - Team-specific documentation
  - `customers` - Customer stories and case studies
  - `culture` - Culture and values
  - `processes` - Company processes
  - `products` - Product documentation

**Supported File Extensions:**
- `*.md` - Markdown files (most common)
- `*.mdx` - MDX files (Markdown with React)
- `*.txt` - Plain text files
- `*.rst` - ReStructuredText files
- `*.org` - Org-mode files

#### GitHub Integration

```yaml
data_sources:
  github:
    enabled: true                  # Set to true to include GitHub data
    issues_path: "/path/to/issues" # Path to exported GitHub issues
    include_comments: true         # Include issue comments
```

**GitHub Setup:**
1. Export GitHub issues to markdown format
2. Place them in a directory
3. Point `issues_path` to that directory
4. GitHub issues provide valuable customer feedback and feature requests

### Team Configuration

```yaml
target_teams:
  - name: "team_name"              # REQUIRED: Team identifier
    keywords: ["keyword1", "key2"] # REQUIRED: Keywords that identify this team
    aliases: ["alias1", "alias2"]  # OPTIONAL: Alternative names
```

#### Example Team Configurations

**Technology Company:**
```yaml
target_teams:
  - name: "platform"
    keywords: ["platform", "infrastructure", "backend", "api", "services"]
    aliases: ["infra", "backend-team"]
    
  - name: "frontend"
    keywords: ["frontend", "ui", "react", "web", "client"]
    aliases: ["ui-team", "web-team"]
    
  - name: "data"
    keywords: ["data", "analytics", "ml", "machine learning", "ai"]
    aliases: ["data-science", "ml-team"]
```

**Consulting Firm:**
```yaml
target_teams:
  - name: "strategy"
    keywords: ["strategy", "consulting", "analysis", "frameworks"]
    aliases: ["strategy-team", "consulting"]
    
  - name: "implementation"
    keywords: ["implementation", "delivery", "execution", "project"]
    aliases: ["delivery", "execution"]
```

**Startup:**
```yaml
target_teams:
  - name: "product"
    keywords: ["product", "pm", "roadmap", "features"]
    aliases: ["product-team"]
    
  - name: "engineering"
    keywords: ["engineering", "development", "technical"]
    aliases: ["eng", "dev"]
```

### Content Categories

```yaml
content_categories:
  category_name:
    keywords: ["keyword1", "keyword2"]  # Words that identify this category
    importance: "high"                  # high, medium, low
```

#### Standard Categories

```yaml
content_categories:
  company_culture:
    keywords: ["values", "culture", "mission", "vision", "principles"]
    importance: "high"
    
  team_documentation:
    keywords: ["team", "responsibilities", "processes", "objectives"]
    importance: "high"
    
  customer_stories:
    keywords: ["customer", "case study", "implementation", "success"]
    importance: "high"
    
  product_strategy:
    keywords: ["strategy", "roadmap", "priorities", "competitive"]
    importance: "high"
    
  technical_docs:
    keywords: ["api", "technical", "implementation", "architecture"]
    importance: "medium"
```

### Processing Configuration

```yaml
processing:
  max_chunk_size: 1200            # Maximum tokens per chunk
  chunk_overlap: 250              # Token overlap between chunks
  batch_size: 40                  # Processing batch size
  max_memory_usage: 0.8           # Memory threshold for cleanup
  embedding_model: "model_name"   # Sentence transformer model
  language: "en"                  # Primary language
```

#### Performance Tuning

**For Limited Memory (4-8GB RAM):**
```yaml
processing:
  max_chunk_size: 800
  chunk_overlap: 150
  batch_size: 16
  max_memory_usage: 0.7
```

**For High Performance (16+ GB RAM):**
```yaml
processing:
  max_chunk_size: 1500
  chunk_overlap: 300
  batch_size: 64
  max_memory_usage: 0.85
```

**For Speed (Faster Processing):**
```yaml
processing:
  embedding_model: "all-MiniLM-L6-v2"  # Fastest
  batch_size: 64
```

**For Quality (Better Embeddings):**
```yaml
processing:
  embedding_model: "all-mpnet-base-v2"  # Higher quality, slower
  batch_size: 32
```

### ChromaDB Configuration

```yaml
chromadb:
  host: "localhost"               # ChromaDB host
  port: 8000                     # ChromaDB port
  collection_name: "knowledge"   # Base collection name
  
  # Feature toggles
  enable_customer_context: true      # Track customer mentions
  enable_team_mapping: true          # Map content to teams
  enable_pain_point_detection: true  # Find problems
  enable_value_proposition_extraction: true  # Find solutions
```

### Quality Control

```yaml
quality:
  min_content_length: 100         # Minimum characters to process
  skip_empty_files: true          # Skip files with no content
  validate_markdown: true         # Validate markdown syntax
  exclude_patterns:               # Files/directories to skip
    - "node_modules/**"
    - ".git/**"
    - "*.tmp"
    - "**/archive/**"
```

#### Common Exclude Patterns

```yaml
exclude_patterns:
  # Build artifacts
  - "node_modules/**"
  - "build/**"
  - "dist/**"
  
  # Version control
  - ".git/**"
  - ".svn/**"
  
  # Temporary files
  - "*.tmp"
  - "*.backup"
  - "*.log"
  
  # Archived content
  - "**/archive/**"
  - "**/old/**"
  - "**/deprecated/**"
  
  # Sensitive content
  - "**/confidential/**"
  - "**/legal/**"
  - "**/private/**"
```

## 🏢 Organization-Specific Configurations

### Startup Company Configuration

**Focus:** Culture, product vision, rapid growth

```yaml
organization:
  name: "YourStartup"

rag_goals:
  primary_purpose: "interview_preparation"
  focus_areas:
    - "company_culture"
    - "product_strategy"
    - "team_dynamics"
  target_role: "product_manager"

target_teams:
  - name: "product"
    keywords: ["product", "pm", "roadmap", "features"]
  - name: "engineering"
    keywords: ["engineering", "development", "technical"]
  - name: "growth"
    keywords: ["growth", "marketing", "acquisition"]

processing:
  max_chunk_size: 1000      # Smaller for faster processing
  batch_size: 32
```

### Enterprise Technology Company

**Focus:** Complex systems, multiple products, detailed processes

```yaml
organization:
  name: "TechCorp"

rag_goals:
  primary_purpose: "knowledge_management"
  focus_areas:
    - "technical_architecture"
    - "team_dynamics"
    - "customer_insights"
    - "product_strategy"

target_teams:
  - name: "platform"
    keywords: ["platform", "infrastructure", "backend"]
  - name: "frontend"
    keywords: ["frontend", "ui", "react", "web"]
  - name: "data"
    keywords: ["data", "analytics", "ml", "ai"]
  - name: "security"
    keywords: ["security", "infosec", "compliance"]

processing:
  max_chunk_size: 1500      # Larger for complex technical content
  batch_size: 50
```

### Consulting Firm

**Focus:** Methodologies, client work, professional development

```yaml
organization:
  name: "ConsultingFirm"

rag_goals:
  primary_purpose: "onboarding"
  focus_areas:
    - "company_culture"
    - "methodologies"
    - "client_insights"
  target_role: "consultant"

target_teams:
  - name: "strategy"
    keywords: ["strategy", "consulting", "analysis"]
  - name: "implementation"
    keywords: ["implementation", "delivery", "execution"]

content_categories:
  methodologies:
    keywords: ["methodology", "framework", "approach"]
    importance: "high"
  client_insights:
    keywords: ["client", "case study", "engagement"]
    importance: "high"
```

### Personal Knowledge Base

**Focus:** Personal notes, research, projects

```yaml
organization:
  name: "Personal Knowledge"

rag_goals:
  primary_purpose: "knowledge_management"
  focus_areas:
    - "research_notes"
    - "project_documentation"

target_teams:
  - name: "technical"
    keywords: ["programming", "code", "technical"]
  - name: "research"
    keywords: ["research", "study", "analysis"]

processing:
  max_chunk_size: 800       # Smaller for personal notes
  batch_size: 20
```

## 🔧 Advanced Configuration

### Custom Content Categories

Add categories specific to your organization:

```yaml
content_categories:
  # Standard categories...
  
  # Custom categories
  compliance_docs:
    keywords: ["compliance", "audit", "regulation", "gdpr", "soc2"]
    importance: "high"
    
  customer_support:
    keywords: ["support", "troubleshooting", "faq", "help"]
    importance: "medium"
    
  onboarding_materials:
    keywords: ["onboarding", "new hire", "training", "orientation"]
    importance: "high"
```

### Multi-Language Support

```yaml
processing:
  language: "en"  # Primary language

# For multiple languages, create separate configs
# or extend the system to support multiple languages
```

### Custom Embedding Models

```yaml
processing:
  # Fast and lightweight
  embedding_model: "all-MiniLM-L6-v2"
  
  # Better quality, slower
  embedding_model: "all-mpnet-base-v2"
  
  # Multilingual
  embedding_model: "distiluse-base-multilingual-cased"
  
  # Domain-specific (if available)
  embedding_model: "sentence-transformers/allenai-specter"  # Scientific papers
```

## 🚨 Troubleshooting Configuration

### Validation Errors

**Error: "Organization name is required"**
```yaml
# Fix: Add organization name
organization:
  name: "YourCompany"  # This field is required
```

**Error: "Documentation path not found"**
```yaml
# Fix: Verify the path exists
data_sources:
  documentation:
    base_path: "/correct/path/to/your/docs"
```

**Error: "No focus areas specified"**
```yaml
# Fix: Add at least one focus area
rag_goals:
  focus_areas:
    - "company_culture"  # At least one required
```

### Performance Issues

**Memory Issues:**
```yaml
# Reduce memory usage
processing:
  batch_size: 16          # Smaller batches
  max_memory_usage: 0.7   # Lower threshold
  max_chunk_size: 800     # Smaller chunks
```

**Slow Processing:**
```yaml
# Speed up processing
processing:
  embedding_model: "all-MiniLM-L6-v2"  # Faster model
  batch_size: 64          # Larger batches
```

### Content Quality Issues

**Too Much Irrelevant Content:**
```yaml
# Better filtering
quality:
  min_content_length: 200  # Skip short files
  exclude_patterns:
    - "**/archive/**"      # Skip archived content
    - "**/old/**"          # Skip old content
    - "**/*.backup"        # Skip backup files
```

**Missing Content:**
```yaml
# More inclusive processing
quality:
  min_content_length: 50   # Lower threshold
  skip_empty_files: false  # Process all files
  file_extensions:
    - "*.md"
    - "*.txt"
    - "*.rst"              # Add more file types
```

## 💡 Best Practices

### 1. Start Simple
- Begin with a basic configuration
- Test with a small subset of documentation
- Gradually add complexity

### 2. Use Descriptive Names
- Choose clear organization names
- Use meaningful team names
- Make keywords specific but comprehensive

### 3. Organize Your Documentation
- Structure documentation logically
- Use consistent naming conventions
- Maintain clear directory hierarchies

### 4. Regular Updates
- Update configuration as organization evolves
- Re-run ingestion when documentation changes
- Monitor and adjust performance settings

### 5. Test Thoroughly
- Validate configuration before full setup
- Test queries after ingestion
- Verify team and category mappings

---

**Need help?** Check the [Developer Guide](developer_guide.md) for technical details or the main [README](../README.md) for general usage.
