#!/usr/bin/env python3
"""
Universal Organization Documentation RAG Ingestion System
Configurable for any organization's documentation, team structure, and goals

Features:
- YAML-based configuration
- Multi-source document processing (Markdown, GitHub issues)
- Team-aware content categorization
- Interview preparation support
- Memory-optimized for M1/M2 Macs
- Comprehensive metadata extraction
"""

import os
import json
import logging
import time
import hashlib
import gc
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass
from datetime import datetime

import chromadb
from chromadb.config import Settings
import markdown
from sentence_transformers import SentenceTransformer
import tiktoken
import psutil


@dataclass
class UniversalConfig:
    """Universal configuration loaded from YAML"""
    
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    @property
    def organization_name(self) -> str:
        return self.config['organization']['name']
    
    @property
    def collection_name(self) -> str:
        base_name = self.config['chromadb']['collection_name']
        org_name = self.organization_name.lower().replace(' ', '_')
        return f"{org_name}_{base_name}"
    
    @property
    def docs_path(self) -> str:
        return self.config['data_sources']['documentation']['base_path']
    
    @property
    def github_enabled(self) -> bool:
        return self.config['data_sources'].get('github', {}).get('enabled', False)
    
    @property
    def github_path(self) -> Optional[str]:
        if self.github_enabled:
            return self.config['data_sources']['github'].get('issues_path')
        return None
    
    @property
    def target_teams(self) -> List[Dict[str, Any]]:
        return self.config['target_teams']
    
    @property
    def rag_goals(self) -> Dict[str, Any]:
        return self.config['rag_goals']
    
    @property
    def processing_config(self) -> Dict[str, Any]:
        return self.config['processing']
    
    @property
    def chromadb_config(self) -> Dict[str, Any]:
        return self.config['chromadb']
    
    @property
    def content_categories(self) -> Dict[str, Any]:
        return self.config['content_categories']
    
    @property
    def priority_paths(self) -> List[str]:
        return self.config['data_sources']['documentation'].get('priority_paths', [])
    
    @property
    def file_extensions(self) -> List[str]:
        return self.config['data_sources']['documentation'].get('file_extensions', ['*.md'])


class UniversalInsightExtractor:
    """Extract insights based on configurable goals and teams"""
    
    def __init__(self, config: UniversalConfig):
        self.config = config
        self.setup_keywords()
    
    def setup_keywords(self):
        """Setup keywords based on configuration"""
        # Generic pain point keywords
        self.pain_point_keywords = [
            "problem", "issue", "challenge", "difficult", "pain", "struggle", 
            "frustrating", "blocking", "slow", "expensive", "complex", "confusing",
            "broken", "not working", "error", "bug", "crash", "failing"
        ]
        
        # Generic value keywords
        self.value_keywords = [
            "solved", "improved", "better", "faster", "easier", "saved", 
            "increased", "reduced", "helped", "enabled", "streamlined",
            "love", "amazing", "great", "perfect", "exactly what we needed"
        ]
        
        # Build team keywords from config
        self.team_keywords = {}
        for team in self.config.target_teams:
            team_name = team['name']
            keywords = team['keywords'] + team.get('aliases', [])
            self.team_keywords[team_name] = keywords
        
        # Customer context keywords (universal)
        self.customer_context_keywords = [
            "customer", "user", "client", "company", "startup", "enterprise",
            "use case", "implementation", "migration", "adoption", "customer request",
            "customer feedback", "customer wants", "customer needs"
        ]
    
    def extract_insights(self, content: str, content_type: str) -> Dict[str, Any]:
        """Extract insights from content based on configuration"""
        insights = {
            "has_pain_points": False,
            "has_value_proposition": False,
            "mentions_teams": [],
            "customer_context": False,
            "complexity_level": "unknown"
        }
        
        content_lower = content.lower()
        
        # Check for pain points
        insights["has_pain_points"] = any(keyword in content_lower for keyword in self.pain_point_keywords)
        
        # Check for value propositions  
        insights["has_value_proposition"] = any(keyword in content_lower for keyword in self.value_keywords)
        
        # Check mentions of teams
        for team_name, keywords in self.team_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                insights["mentions_teams"].append(team_name)
        
        # Check for customer context
        insights["customer_context"] = any(keyword in content_lower for keyword in self.customer_context_keywords)
        
        # Determine complexity level
        if "beginner" in content_lower or "getting started" in content_lower:
            insights["complexity_level"] = "beginner"
        elif "advanced" in content_lower or "enterprise" in content_lower:
            insights["complexity_level"] = "advanced"
        elif "api" in content_lower or "technical" in content_lower:
            insights["complexity_level"] = "technical"
        else:
            insights["complexity_level"] = "intermediate"
        
        return insights


class MemoryMonitor:
    """Monitor memory usage and trigger cleanup when needed"""
    
    def __init__(self, max_usage: float = 0.8):
        self.max_usage = max_usage
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> float:
        """Get current memory usage as percentage of total system memory"""
        memory_info = self.process.memory_info()
        total_memory = psutil.virtual_memory().total
        return memory_info.rss / total_memory
    
    def check_and_cleanup(self):
        """Check memory usage and trigger cleanup if needed"""
        usage = self.get_memory_usage()
        if usage > self.max_usage:
            logging.warning(f"Memory usage high: {usage:.1%}, triggering cleanup")
            gc.collect()
            time.sleep(1)
            new_usage = self.get_memory_usage()
            logging.info(f"Memory usage after cleanup: {new_usage:.1%}")


class UniversalDocumentProcessor:
    """Universal processor for organization documentation"""
    
    def __init__(self, config: UniversalConfig):
        self.config = config
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.insight_extractor = UniversalInsightExtractor(config)
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def determine_content_category(self, file_path: Path, content: str = "") -> str:
        """Determine content category based on configuration"""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        # Check each configured category
        for category, config in self.config.content_categories.items():
            keywords = config.get('keywords', [])
            
            # Check path-based matching
            if any(keyword in path_str for keyword in keywords):
                return category
            
            # Check content-based matching for categories with keywords
            if keywords and any(keyword in content_lower for keyword in keywords):
                return category
        
        # Special handling for GitHub issues
        if "github" in path_str or "issue" in path_str:
            return "github_issue"
        
        # Default fallback
        return "general_docs"
    
    def extract_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Extract frontmatter from markdown content"""
        frontmatter = {}
        
        if content.startswith('---'):
            try:
                _, fm_content, main_content = content.split('---', 2)
                for line in fm_content.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"\'')
                return frontmatter, main_content.strip()
            except:
                pass
        
        return frontmatter, content
    
    def markdown_to_text(self, content: str) -> str:
        """Convert markdown to plain text"""
        html = markdown.markdown(content)
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def parse_github_issue_metadata(self, content: str) -> Dict[str, Any]:
        """Parse metadata from GitHub issue markdown"""
        metadata = {}
        
        # Extract common GitHub issue metadata
        patterns = {
            'issue_number': r'Issue Number:\*\*\s*#?(\d+)',
            'state': r'State:\*\*\s*(\w+)',
            'author': r'Author:\*\*\s*@?([^\n]+)',
            'created_at': r'Created:\*\*\s*([^\n]+)',
            'updated_at': r'Updated:\*\*\s*([^\n]+)',
            'comment_count': r'Total Comments:\*\*\s*(\d+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1).strip()
                if key in ['issue_number', 'comment_count']:
                    metadata[key] = int(value)
                else:
                    metadata[key] = value
        
        # Extract labels
        labels_match = re.search(r'Labels:\*\*\s*(.+)', content)
        if labels_match:
            labels_text = labels_match.group(1)
            labels = re.findall(r'`([^`]+)`', labels_text)
            metadata["labels"] = labels
        else:
            metadata["labels"] = []
        
        # Extract title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()
        
        return metadata
    
    def enhance_metadata_with_teams(self, content: str, labels: List[str] = None) -> Dict[str, Any]:
        """Add team-specific metadata based on configuration"""
        enhanced = {}
        content_lower = content.lower()
        labels = labels or []
        
        # Check team ownership
        team_ownership = "unknown"
        for team in self.config.target_teams:
            team_name = team['name']
            keywords = team['keywords'] + team.get('aliases', [])
            
            # Check labels for team indicators
            if any(f"team-{team_name}" in label or f"team/{team_name}" in label for label in labels):
                team_ownership = team_name
                break
            
            # Check content for team keywords
            if any(keyword in content_lower for keyword in keywords):
                team_ownership = team_name
                break
        
        enhanced['team_ownership'] = team_ownership
        
        # Add team-specific flags
        for team in self.config.target_teams:
            team_name = team['name']
            team_flag = f"relates_to_{team_name.replace('-', '_')}"
            enhanced[team_flag] = (team_ownership == team_name)
        
        return enhanced
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        max_chunk_size = self.config.processing_config.get('max_chunk_size', 1000)
        chunk_overlap = self.config.processing_config.get('chunk_overlap', 200)
        
        chunks = []
        tokens = self.tokenizer.encode(text)
        
        if len(tokens) <= max_chunk_size:
            # Single chunk
            insights = self.insight_extractor.extract_insights(text, metadata.get("content_category", ""))
            
            chunks.append({
                "content": text,
                "metadata": {
                    **metadata, 
                    **insights,
                    "chunk_index": 0, 
                    "total_chunks": 1,
                    "token_count": len(tokens)
                }
            })
            return chunks
        
        # Split into overlapping chunks
        chunk_index = 0
        start = 0
        
        while start < len(tokens):
            end = min(start + max_chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            # Extract insights for this chunk
            insights = self.insight_extractor.extract_insights(chunk_text, metadata.get("content_category", ""))
            
            chunk_metadata = {
                **metadata,
                **insights,
                "chunk_index": chunk_index,
                "chunk_start_token": start,
                "chunk_end_token": end,
                "token_count": len(chunk_tokens)
            }
            
            chunks.append({
                "content": chunk_text,
                "metadata": chunk_metadata
            })
            
            chunk_index += 1
            start = end - chunk_overlap
            
            if start >= len(tokens) - chunk_overlap:
                break
        
        # Update total_chunks in all chunks
        for chunk in chunks:
            chunk["metadata"]["total_chunks"] = len(chunks)
            
        return chunks
    
    def process_markdown_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process markdown file with universal metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            frontmatter, main_content = self.extract_frontmatter(content)
            
            # Convert to plain text
            text = self.markdown_to_text(main_content)
            
            # Determine content category
            content_category = self.determine_content_category(file_path, text)
            
            # Create base metadata
            metadata = {
                "content_type": "documentation",
                "content_category": content_category,
                "source_file": str(file_path.relative_to(Path(self.config.docs_path))),
                "file_path": str(file_path),
                "title": frontmatter.get("title", file_path.stem),
                "file_extension": file_path.suffix,
                "organization": self.config.organization_name,
                **frontmatter
            }
            
            # Add team-specific metadata
            team_metadata = self.enhance_metadata_with_teams(text)
            metadata.update(team_metadata)
            
            # Determine relevance based on goals
            is_relevant = self.is_content_relevant(content_category, text)
            metadata['is_goal_relevant'] = is_relevant
            
            return self.chunk_text(text, metadata)
            
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
            return []
    
    def process_github_issue(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process GitHub issue markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse issue metadata
            issue_metadata = self.parse_github_issue_metadata(content)
            
            # Clean content for processing
            description_start = re.search(r'## Issue Description', content)
            if description_start:
                clean_content = content[description_start.start():]
            else:
                clean_content = content
            
            # Convert to plain text
            text = self.markdown_to_text(clean_content)
            
            # Create metadata
            labels = issue_metadata.get('labels', [])
            title = issue_metadata.get('title', file_path.stem)
            
            metadata = {
                "content_type": "github_issue",
                "content_category": "product_feedback",
                "source_file": str(file_path.name),
                "file_path": str(file_path),
                "title": title,
                "labels": labels,
                "organization": self.config.organization_name,
                **issue_metadata
            }
            
            # Add team-specific metadata
            team_metadata = self.enhance_metadata_with_teams(text, labels)
            metadata.update(team_metadata)
            
            # Always relevant for goal-oriented processing
            metadata['is_goal_relevant'] = True
            
            return self.chunk_text(text, metadata)
            
        except Exception as e:
            logging.error(f"Error processing GitHub issue {file_path}: {e}")
            return []
    
    def is_content_relevant(self, category: str, content: str) -> bool:
        """Determine if content is relevant based on RAG goals"""
        focus_areas = self.config.rag_goals.get('focus_areas', [])
        
        # High-priority categories are always relevant
        high_priority_categories = [
            'company_culture', 'team_documentation', 'customer_stories', 'product_strategy'
        ]
        
        if category in high_priority_categories:
            return True
        
        # Check if content relates to focus areas
        content_lower = content.lower()
        relevance_keywords = {
            'company_culture': ['culture', 'values', 'mission', 'principles'],
            'team_dynamics': ['team', 'collaboration', 'process', 'structure'],
            'customer_insights': ['customer', 'user', 'feedback', 'problem'],
            'product_strategy': ['strategy', 'roadmap', 'competitive', 'priorities']
        }
        
        for focus_area in focus_areas:
            if focus_area in relevance_keywords:
                keywords = relevance_keywords[focus_area]
                if any(keyword in content_lower for keyword in keywords):
                    return True
        
        return False


class UniversalChromaDBIngester:
    """Universal ChromaDB operations"""
    
    def __init__(self, config: UniversalConfig):
        self.config = config
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.memory_monitor = MemoryMonitor(config.processing_config.get('max_memory_usage', 0.8))
        
    def connect(self):
        """Connect to ChromaDB"""
        try:
            chromadb_config = self.config.chromadb_config
            self.client = chromadb.HttpClient(
                host=chromadb_config.get('host', 'localhost'),
                port=chromadb_config.get('port', 8000),
                settings=Settings(allow_reset=True)
            )
            
            self.client.heartbeat()
            logging.info("Successfully connected to ChromaDB")
            
            # Create or get collection
            collection_name = self.config.collection_name
            try:
                self.collection = self.client.get_collection(collection_name)
                logging.info(f"Found existing collection: {collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={
                        "description": f"{self.config.organization_name} knowledge base",
                        "organization": self.config.organization_name,
                        "purpose": self.config.rag_goals.get('primary_purpose', 'knowledge_management'),
                        "focus_areas": ','.join(self.config.rag_goals.get('focus_areas', [])),
                        "created_at": datetime.now().isoformat()
                    }
                )
                logging.info(f"Created new collection: {collection_name}")
                
        except Exception as e:
            logging.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    def load_embedding_model(self):
        """Load embedding model with cross-platform compatibility"""
        try:
            model_name = self.config.processing_config.get('embedding_model', 'all-MiniLM-L6-v2')
            logging.info(f"Loading embedding model: {model_name}")
            
            # Handle PyTorch device compatibility
            import torch
            
            device = None
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = "mps"  # M1/M2 Mac
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
            
            logging.info(f"Using device: {device}")
            
            try:
                self.embedding_model = SentenceTransformer(model_name, device=device)
            except:
                logging.warning("Device-specific loading failed, trying CPU-only...")
                self.embedding_model = SentenceTransformer(model_name, device="cpu")
            
            # Test the model
            test_embedding = self.embedding_model.encode(["Test embedding generation"])
            logging.info(f"Model loaded successfully, embedding shape: {test_embedding.shape}")
            
        except Exception as e:
            logging.error(f"Failed to load embedding model: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with optimal batch sizing"""
        try:
            batch_size = self.config.processing_config.get('batch_size', 32)
            
            embeddings = self.embedding_model.encode(
                texts,
                convert_to_tensor=False,
                show_progress_bar=True,
                batch_size=min(batch_size, 16),  # Conservative batch size
                normalize_embeddings=True
            )
            return embeddings.tolist()
        except Exception as e:
            logging.error(f"Failed to generate embeddings: {e}")
            raise
    
    def clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata for ChromaDB compatibility"""
        cleaned = {}
        for key, value in metadata.items():
            if isinstance(value, list):
                cleaned[key] = ", ".join(str(v) for v in value) if value else ""
            elif isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            elif value is None:
                cleaned[key] = ""
            else:
                cleaned[key] = str(value)
        return cleaned
    
    def ingest_batch(self, chunks: List[Dict[str, Any]]) -> bool:
        """Ingest batch of chunks"""
        try:
            if not chunks:
                return True
            
            texts = [chunk["content"] for chunk in chunks]
            metadatas = [self.clean_metadata(chunk["metadata"]) for chunk in chunks]
            
            # Generate unique IDs
            ids = []
            for i, chunk in enumerate(chunks):
                content_hash = hashlib.md5(chunk["content"].encode()).hexdigest()[:8]
                content_type = chunk['metadata']['content_type']
                org_name = self.config.organization_name.lower().replace(' ', '_')
                chunk_id = f"{org_name}_{content_type}_{content_hash}_{i}"
                ids.append(chunk_id)
            
            # Log statistics
            original_metadatas = [chunk["metadata"] for chunk in chunks]
            relevant_count = sum(1 for m in original_metadatas if m.get('is_goal_relevant', False))
            
            logging.info(f"Batch: {len(chunks)} chunks, {relevant_count} goal-relevant")
            
            # Generate embeddings and add to collection
            embeddings = self.generate_embeddings(texts)
            
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
            self.memory_monitor.check_and_cleanup()
            return True
            
        except Exception as e:
            logging.error(f"Failed to ingest batch: {e}")
            return False


def setup_logging(config: UniversalConfig):
    """Setup logging based on configuration"""
    log_level = getattr(logging, config.config['output'].get('log_level', 'INFO'))
    log_file = config.config['output'].get('log_file', 'ingestion.log')
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def get_markdown_files(config: UniversalConfig) -> Iterator[Path]:
    """Get markdown files with priority ordering"""
    docs_dir = Path(config.docs_path)
    processed_files = set()
    
    # First, process priority paths
    for priority_path in config.priority_paths:
        priority_dir = docs_dir / priority_path
        if priority_dir.exists():
            for ext in config.file_extensions:
                for file_path in priority_dir.rglob(ext):
                    if file_path.is_file() and file_path not in processed_files:
                        processed_files.add(file_path)
                        yield file_path
    
    # Then process remaining files
    for ext in config.file_extensions:
        for file_path in docs_dir.rglob(ext):
            if file_path.is_file() and file_path not in processed_files:
                yield file_path


def get_github_issue_files(github_path: str) -> Iterator[Path]:
    """Get GitHub issue markdown files"""
    github_dir = Path(github_path)
    if not github_dir.exists():
        logging.warning(f"GitHub directory does not exist: {github_path}")
        return
    
    for file_path in github_dir.glob("*.md"):
        if file_path.is_file():
            yield file_path


def main(config_path: str = "config.yaml"):
    """Main ingestion process"""
    
    # Load configuration
    try:
        config = UniversalConfig(config_path)
    except Exception as e:
        print(f"Error loading configuration from {config_path}: {e}")
        return
    
    setup_logging(config)
    
    logging.info(f"🚀 Starting {config.organization_name} Knowledge Ingestion")
    logging.info(f"🎯 Purpose: {config.rag_goals.get('primary_purpose', 'knowledge_management')}")
    logging.info(f"📋 Focus areas: {', '.join(config.rag_goals.get('focus_areas', []))}")
    
    processor = UniversalDocumentProcessor(config)
    ingester = UniversalChromaDBIngester(config)
    
    try:
        # Connect and setup
        ingester.connect()
        ingester.load_embedding_model()
        
        total_chunks = 0
        relevant_chunks = 0
        batch_size = config.processing_config.get('batch_size', 32)
        progress_interval = config.config['output'].get('progress_interval', 50)
        
        # Process documentation
        logging.info("📚 Processing documentation...")
        doc_files = list(get_markdown_files(config))
        logging.info(f"Found {len(doc_files)} documentation files")
        
        batch_chunks = []
        for i, file_path in enumerate(doc_files):
            if i % progress_interval == 0:
                logging.info(f"Processing file {i+1}/{len(doc_files)}: {file_path.name}")
            
            chunks = processor.process_markdown_file(file_path)
            batch_chunks.extend(chunks)
            
            # Count relevant content
            relevant_in_file = sum(1 for chunk in chunks if chunk['metadata'].get('is_goal_relevant', False))
            relevant_chunks += relevant_in_file
            
            if len(batch_chunks) >= batch_size:
                if ingester.ingest_batch(batch_chunks):
                    total_chunks += len(batch_chunks)
                batch_chunks = []
        
        if batch_chunks:
            if ingester.ingest_batch(batch_chunks):
                total_chunks += len(batch_chunks)
        
        logging.info(f"📚 Documentation complete: {relevant_chunks} relevant chunks")
        
        # Process GitHub issues if enabled
        if config.github_enabled and config.github_path:
            logging.info("🐛 Processing GitHub issues...")
            github_files = list(get_github_issue_files(config.github_path))
            logging.info(f"Found {len(github_files)} GitHub issue files")
            
            batch_chunks = []
            for i, file_path in enumerate(github_files):
                if i % progress_interval == 0:
                    logging.info(f"Processing issue {i+1}/{len(github_files)}: {file_path.name}")
                
                chunks = processor.process_github_issue(file_path)
                batch_chunks.extend(chunks)
                
                if len(batch_chunks) >= batch_size:
                    if ingester.ingest_batch(batch_chunks):
                        total_chunks += len(batch_chunks)
                    batch_chunks = []
            
            if batch_chunks:
                if ingester.ingest_batch(batch_chunks):
                    total_chunks += len(batch_chunks)
        
        # Final statistics
        collection_count = ingester.collection.count()
        
        logging.info("🎉 Ingestion Complete!")
        logging.info(f"📊 Total chunks processed: {total_chunks}")
        logging.info(f"📊 Relevant chunks: {relevant_chunks}")
        logging.info(f"📊 Collection contains: {collection_count} documents")
        logging.info(f"🎯 Ready for {config.rag_goals.get('primary_purpose', 'knowledge queries')}!")
        
    except Exception as e:
        logging.error(f"❌ Ingestion failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    main(config_path)
