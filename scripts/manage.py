#!/usr/bin/env python3
"""
Universal RAG Management Tool
Common operations for managing your organization's knowledge base
"""

import yaml
import chromadb
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

class RAGManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        if not self.config:
            sys.exit(1)
        
        self.org_name = self.config['organization']['name']
        self.client = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return None
    
    def get_collection_name(self) -> str:
        """Get collection name from config"""
        org_name = self.org_name.lower().replace(' ', '_')
        base_name = self.config['chromadb']['collection_name']
        return f"{org_name}_{base_name}"
    
    def connect_to_chromadb(self) -> bool:
        """Connect to ChromaDB"""
        try:
            chromadb_config = self.config['chromadb']
            self.client = chromadb.HttpClient(
                host=chromadb_config.get('host', 'localhost'),
                port=chromadb_config.get('port', 8000)
            )
            self.client.heartbeat()
            return True
        except Exception as e:
            print(f"❌ Failed to connect to ChromaDB: {e}")
            return False
    
    def get_docker_compose_command(self) -> str:
        """Detect and return the correct Docker Compose command"""
        try:
            subprocess.run(['docker', 'compose', 'version'], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return 'docker compose'
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(['docker-compose', 'version'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                return 'docker-compose'
            except (subprocess.CalledProcessError, FileNotFoundError):
                return None
    
    def status(self):
        """Show status of the RAG system"""
        print(f"📊 {self.org_name} RAG System Status")
        print("=" * 50)
        
        # Check Docker
        compose_cmd = self.get_docker_compose_command()
        if compose_cmd:
            print(f"✅ Docker Compose: {compose_cmd}")
        else:
            print("❌ Docker Compose: Not available")
            return
        
        # Check ChromaDB container
        try:
            result = subprocess.run([*compose_cmd.split(), 'ps'], 
                                  capture_output=True, text=True, check=True)
            if 'chromadb' in result.stdout and 'Up' in result.stdout:
                print("✅ ChromaDB Container: Running")
            else:
                print("❌ ChromaDB Container: Not running")
                print("   Run: ./setup.sh or manage.py start")
                return
        except subprocess.CalledProcessError:
            print("❌ ChromaDB Container: Cannot check status")
            return
        
        # Check ChromaDB API
        if self.connect_to_chromadb():
            print("✅ ChromaDB API: Responding")
            
            # Check collection
            try:
                collection_name = self.get_collection_name()
                collection = self.client.get_collection(collection_name)
                count = collection.count()
                print(f"✅ Knowledge Collection: {collection_name} ({count} documents)")
                
                # Analyze content
                if count > 0:
                    sample = collection.get(limit=min(100, count))
                    if sample['metadatas']:
                        categories = {}
                        relevant_count = 0
                        for metadata in sample['metadatas']:
                            category = metadata.get('content_category', 'unknown')
                            categories[category] = categories.get(category, 0) + 1
                            if metadata.get('is_goal_relevant', False):
                                relevant_count += 1
                        
                        print(f"📈 Content Analysis (sample of {len(sample['metadatas'])}):")
                        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
                            print(f"   {category}: {count}")
                        print(f"   Goal-relevant: {relevant_count}/{len(sample['metadatas'])}")
                
            except Exception as e:
                print(f"⚠️  Knowledge Collection: {collection_name} not found")
                print("   Run ingestion: python ingest_data.py")
        else:
            print("❌ ChromaDB API: Not responding")
        
        # Configuration info
        print(f"\n⚙️  Configuration:")
        print(f"   File: {self.config_path}")
        print(f"   Purpose: {self.config['rag_goals'].get('primary_purpose')}")
        print(f"   Focus: {', '.join(self.config['rag_goals'].get('focus_areas', []))}")
    
    def start(self):
        """Start the RAG system"""
        print(f"🚀 Starting {self.org_name} RAG System...")
        
        compose_cmd = self.get_docker_compose_command()
        if not compose_cmd:
            print("❌ Docker Compose not available")
            return
        
        try:
            result = subprocess.run([*compose_cmd.split(), 'up', '-d'], 
                                  capture_output=True, text=True, check=True)
            print("✅ ChromaDB container started")
            
            # Wait for ChromaDB to be ready
            print("⏳ Waiting for ChromaDB to be ready...")
            max_attempts = 30
            for attempt in range(max_attempts):
                if self.connect_to_chromadb():
                    print("✅ ChromaDB is ready!")
                    break
                time.sleep(2)
                if attempt % 5 == 0:
                    print(f"   Attempt {attempt + 1}/{max_attempts}...")
            else:
                print("⚠️  ChromaDB may still be starting up")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start: {e}")
            print(f"   Output: {e.stderr}")
    
    def stop(self):
        """Stop the RAG system"""
        print(f"🛑 Stopping {self.org_name} RAG System...")
        
        compose_cmd = self.get_docker_compose_command()
        if not compose_cmd:
            print("❌ Docker Compose not available")
            return
        
        try:
            subprocess.run([*compose_cmd.split(), 'down'], check=True)
            print("✅ ChromaDB container stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stop: {e}")
    
    def restart(self):
        """Restart the RAG system"""
        print(f"🔄 Restarting {self.org_name} RAG System...")
        self.stop()
        time.sleep(2)
        self.start()
    
    def logs(self):
        """Show ChromaDB logs"""
        print(f"📋 {self.org_name} ChromaDB Logs:")
        print("=" * 50)
        
        compose_cmd = self.get_docker_compose_command()
        if not compose_cmd:
            print("❌ Docker Compose not available")
            return
        
        try:
            subprocess.run([*compose_cmd.split(), 'logs', '-f', 'chromadb'])
        except KeyboardInterrupt:
            print("\n📋 Log viewing stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to show logs: {e}")
    
    def reset(self):
        """Reset the RAG system (WARNING: Deletes all data)"""
        collection_name = self.get_collection_name()
        
        print(f"⚠️  WARNING: This will delete all data in {collection_name}")
        print(f"   Organization: {self.org_name}")
        print(f"   Collection: {collection_name}")
        
        confirm = input("\nType 'DELETE' to confirm reset: ").strip()
        if confirm != 'DELETE':
            print("❌ Reset cancelled")
            return
        
        print(f"🗑️  Resetting {self.org_name} RAG System...")
        
        # Stop ChromaDB
        self.stop()
        
        # Remove data volumes
        compose_cmd = self.get_docker_compose_command()
        if compose_cmd:
            try:
                subprocess.run([*compose_cmd.split(), 'down', '--volumes'], check=True)
                print("✅ Data volumes removed")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Volume removal failed: {e}")
        
        # Start fresh
        self.start()
        
        print("✅ RAG system reset complete")
        print("💡 Run ingestion to rebuild: python ingest_data.py")
    
    def ingest(self):
        """Run data ingestion"""
        print(f"📚 Starting {self.org_name} data ingestion...")
        
        try:
            subprocess.run(['python', 'ingest_data.py', self.config_path], check=True)
            print("✅ Ingestion completed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ingestion failed: {e}")
            print("💡 Check the logs for details")
    
    def test(self):
        """Run system tests"""
        print(f"🧪 Testing {self.org_name} RAG System...")
        
        try:
            subprocess.run(['python', 'test_setup.py', self.config_path], check=True)
            print("✅ Tests completed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Tests failed: {e}")
    
    def backup(self):
        """Create a backup of the knowledge base"""
        print(f"💾 Creating backup of {self.org_name} knowledge base...")
        
        if not self.connect_to_chromadb():
            print("❌ Cannot connect to ChromaDB for backup")
            return
        
        try:
            collection_name = self.get_collection_name()
            collection = self.client.get_collection(collection_name)
            
            # Get all documents
            all_docs = collection.get()
            
            import json
            from datetime import datetime
            
            backup_data = {
                'organization': self.org_name,
                'collection_name': collection_name,
                'backup_date': datetime.now().isoformat(),
                'document_count': len(all_docs['documents']),
                'documents': all_docs['documents'],
                'metadatas': all_docs['metadatas'],
                'ids': all_docs['ids']
            }
            
            backup_file = f"backup_{self.org_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"✅ Backup created: {backup_file}")
            print(f"📊 Backed up {backup_data['document_count']} documents")
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Universal RAG Management Tool")
    parser.add_argument('--config', '-c', default='config.yaml', 
                       help='Configuration file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add subcommands
    subparsers.add_parser('status', help='Show system status')
    subparsers.add_parser('start', help='Start the RAG system')
    subparsers.add_parser('stop', help='Stop the RAG system')
    subparsers.add_parser('restart', help='Restart the RAG system')
    subparsers.add_parser('logs', help='Show ChromaDB logs')
    subparsers.add_parser('reset', help='Reset the system (deletes all data)')
    subparsers.add_parser('ingest', help='Run data ingestion')
    subparsers.add_parser('test', help='Run system tests')
    subparsers.add_parser('backup', help='Create a backup of the knowledge base')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check config file exists
    if not Path(args.config).exists():
        print(f"❌ Configuration file not found: {args.config}")
        return
    
    # Create manager and run command
    manager = RAGManager(args.config)
    
    if args.command == 'status':
        manager.status()
    elif args.command == 'start':
        manager.start()
    elif args.command == 'stop':
        manager.stop()
    elif args.command == 'restart':
        manager.restart()
    elif args.command == 'logs':
        manager.logs()
    elif args.command == 'reset':
        manager.reset()
    elif args.command == 'ingest':
        manager.ingest()
    elif args.command == 'test':
        manager.test()
    elif args.command == 'backup':
        manager.backup()

if __name__ == "__main__":
    main()
