# Deployment Guide

This guide covers deploying the Universal Organization RAG System in different environments.

## 🏠 Local Development

### Single User Setup

Perfect for personal use or testing:

```bash
# Standard local setup
git clone <repository-url>
cd universal-org-rag
cp config_examples/personal_knowledge.yaml config.yaml
# Edit config.yaml with your paths
./setup.sh
```

**Characteristics:**
- ChromaDB runs on localhost:8000
- Data stored in local `chroma_data/` directory
- Suitable for 1-10GB of documentation
- No authentication required

### Multi-User Local Setup

For small teams sharing a machine:

```bash
# Use a shared configuration
cp config_examples/tech_company.yaml config.yaml

# Edit for shared paths
nano config.yaml
```

```yaml
data_sources:
  documentation:
    base_path: "/shared/company/docs"  # Shared documentation path

organization:
  name: "SharedCompany"
```

## 🌐 Team Deployment

### Docker-Based Team Setup

Deploy for team access with persistent data:

#### 1. Server Setup

```bash
# On your team server
git clone <repository-url>
cd universal-org-rag

# Configure for team use
cp config_examples/tech_company.yaml config.yaml
```

#### 2. Configuration for Team Access

```yaml
# config.yaml
organization:
  name: "YourTeam"

data_sources:
  documentation:
    base_path: "/opt/team/docs"  # Shared documentation location

chromadb:
  host: "0.0.0.0"  # Allow external connections
  port: 8000
```

#### 3. Docker Compose for Production

```yaml
# docker-compose.production.yml
version: '3.8'
services:
  chromadb:
    image: chromadb/chroma:0.4.24
    container_name: team-chromadb
    ports:
      - "8000:8000"
    volumes:
      - ./chroma_data:/chroma/chroma
      - /opt/team/docs:/data/docs:ro  # Mount team docs as read-only
    environment:
      - ANONYMIZED_TELEMETRY=False
      - IS_PERSISTENT=TRUE
      - PERSIST_DIRECTORY=/chroma/chroma
      - CHROMA_SERVER_CORS_ALLOW_ORIGINS=["*"]
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

#### 4. Deploy and Ingest

```bash
# Start the service
docker compose -f docker-compose.production.yml up -d

# Run ingestion
python ingest_data.py config.yaml

# Test the deployment
python test_setup.py config.yaml
```

### Reverse Proxy Setup (Optional)

For team access with custom domain:

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/team-rag
server {
    listen 80;
    server_name rag.yourcompany.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/team-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## ☁️ Cloud Deployment

### AWS Deployment

#### EC2 Instance Setup

```bash
# Launch EC2 instance (t3.medium or larger recommended)
# Install Docker and Docker Compose
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Application Deployment

```bash
# Clone and setup
git clone <repository-url>
cd universal-org-rag

# Configure for cloud
cp config_examples/tech_company.yaml config.yaml
# Edit config.yaml for your organization

# Deploy
./setup.sh
```

#### Security Groups

Allow these ports in your AWS Security Group:
- Port 22 (SSH) - for management
- Port 8000 (ChromaDB) - for API access
- Port 80/443 (HTTP/HTTPS) - if using reverse proxy

### Google Cloud Platform

#### Compute Engine Setup

```bash
# Create VM instance
gcloud compute instances create rag-server \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-standard-2 \
    --zone=us-central1-a \
    --tags=rag-server

# SSH and setup
gcloud compute ssh rag-server
```

#### Firewall Rules

```bash
# Allow ChromaDB access
gcloud compute firewall-rules create allow-chromadb \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --target-tags rag-server \
    --description "Allow ChromaDB access"
```

### Docker Hub Deployment

#### Custom Docker Image

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x setup.sh scripts/*.sh scripts/*.py

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "ingest_data.py", "config.yaml"]
```

```bash
# Build and push
docker build -t your-org/universal-rag:latest .
docker push your-org/universal-rag:latest
```

## 🔐 Security Considerations

### Authentication Setup

#### Basic HTTP Authentication (Nginx)

```bash
# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd username

# Update nginx config
```

```nginx
server {
    listen 80;
    server_name rag.yourcompany.com;
    
    auth_basic "RAG System";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://localhost:8000;
        # ... other proxy settings
    }
}
```

#### API Key Protection

For programmatic access, implement API key validation:

```python
# api_wrapper.py
import os
from flask import Flask, request, jsonify, abort
import chromadb

app = Flask(__name__)
VALID_API_KEYS = os.environ.get('RAG_API_KEYS', '').split(',')

def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in VALID_API_KEYS:
        abort(401, 'Invalid API key')

@app.route('/search', methods=['POST'])
def search():
    validate_api_key()
    
    data = request.json
    query = data.get('query')
    
    client = chromadb.HttpClient(host="localhost", port=8000)
    collection = client.get_collection("your_collection")
    results = collection.query(query_texts=[query], n_results=5)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Network Security

#### Firewall Configuration

```bash
# Ubuntu/Debian with ufw
sudo ufw allow ssh
sudo ufw allow 8000  # ChromaDB
sudo ufw allow 80    # HTTP (if using reverse proxy)
sudo ufw allow 443   # HTTPS (if using SSL)
sudo ufw enable

# RHEL/CentOS with firewalld
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

#### SSL/TLS Setup

```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d rag.yourcompany.com
```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash

# Check ChromaDB health
if curl -f http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✅ ChromaDB is healthy"
    exit 0
else
    echo "❌ ChromaDB is down"
    exit 1
fi
EOF

chmod +x health_check.sh

# Add to crontab for monitoring
echo "*/5 * * * * /path/to/health_check.sh" | crontab -
```

### Log Management

```yaml
# docker-compose.production.yml
services:
  chromadb:
    # ... other config
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Backup Strategy

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/rag-system"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup ChromaDB data
docker compose exec chromadb tar czf - /chroma/chroma > "$BACKUP_DIR/chromadb_$DATE.tar.gz"

# Backup configuration
cp config.yaml "$BACKUP_DIR/config_$DATE.yaml"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.yaml" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Schedule daily backups
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

### Performance Monitoring

```python
# monitoring.py
import psutil
import chromadb
import json
import time

def get_system_metrics():
    """Get system performance metrics"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'timestamp': time.time()
    }

def get_chromadb_metrics():
    """Get ChromaDB metrics"""
    try:
        client = chromadb.HttpClient(host="localhost", port=8000)
        collections = client.list_collections()
        
        metrics = {'collections': []}
        for collection in collections:
            collection_obj = client.get_collection(collection.name)
            metrics['collections'].append({
                'name': collection.name,
                'count': collection_obj.count()
            })
        
        return metrics
    except Exception as e:
        return {'error': str(e)}

# Log metrics every hour
if __name__ == '__main__':
    metrics = {
        'system': get_system_metrics(),
        'chromadb': get_chromadb_metrics()
    }
    
    with open('/var/log/rag-metrics.log', 'a') as f:
        f.write(json.dumps(metrics) + '\n')
```

## 🔄 Update and Maintenance

### System Updates

```bash
# Update script
cat > update.sh << 'EOF'
#!/bin/bash

echo "🔄 Updating Universal RAG System..."

# Backup current state
python scripts/manage.py backup

# Pull latest changes
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart services
python scripts/manage.py restart

# Test the update
python test_setup.py config.yaml

echo "✅ Update completed"
EOF

chmod +x update.sh
```

### Data Refresh

```bash
# Data refresh script
cat > refresh_data.sh << 'EOF'
#!/bin/bash

echo "📚 Refreshing knowledge base..."

# Re-ingest data
python ingest_data.py config.yaml

# Validate the refresh
python test_setup.py config.yaml

echo "✅ Data refresh completed"
EOF

chmod +x refresh_data.sh

# Schedule weekly data refresh
echo "0 1 * * 0 /path/to/refresh_data.sh" | crontab -
```

## 🌍 Multi-Environment Setup

### Development/Staging/Production

```yaml
# config.dev.yaml
organization:
  name: "YourCompany-Dev"
chromadb:
  port: 8001

# config.staging.yaml  
organization:
  name: "YourCompany-Staging"
chromadb:
  port: 8002

# config.prod.yaml
organization:
  name: "YourCompany"
chromadb:
  port: 8000
```

```bash
# Deploy to different environments
./setup.sh config.dev.yaml     # Development
./setup.sh config.staging.yaml # Staging  
./setup.sh config.prod.yaml    # Production
```

## 🔧 Troubleshooting Deployments

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Port conflicts | Another service using 8000 | Change port in config/docker-compose |
| Memory issues | Insufficient RAM | Reduce batch_size, add swap |
| Permission errors | Wrong file permissions | `chmod +x` scripts, check Docker permissions |
| Network timeouts | Firewall blocking | Configure firewall rules |
| Data not found | Wrong paths in config | Verify documentation paths exist |

### Debug Commands

```bash
# Check container status
docker compose ps

# View logs
docker compose logs -f chromadb

# Check system resources
python scripts/manage.py status

# Test connectivity
curl http://localhost:8000/api/v1/heartbeat

# Validate configuration
python test_setup.py config.yaml
```

---

**🚀 Your Universal RAG System is now ready for production deployment!**

For specific deployment questions, refer to the [Developer Guide](developer_guide.md) or open an issue in the repository.
