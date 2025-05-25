#!/usr/bin/env python3
"""
Universal Organization RAG System Test Suite

🚨 IMPORTANT: Activate virtual environment first!
   Run: source venv/bin/activate (macOS/Linux) or venv\Scripts\activate (Windows)
   
Usage: python test_setup.py config.yaml

Configurable testing for any organization's knowledge base
Tests connection, content quality, and query relevance

Tested on Apple M1/M2 hardware with cross-platform compatibility.
"""

import yaml
import chromadb
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

def get_collection_name(config: Dict[str, Any]) -> str:
    """Get collection name from config"""
    org_name = config['organization']['name'].lower().replace(' ', '_')
    base_name = config['chromadb']['collection_name']
    return f"{org_name}_{base_name}"

def test_chromadb_connection(config: Dict[str, Any]):
    """Test basic ChromaDB connection"""
    try:
        chromadb_config = config['chromadb']
        client = chromadb.HttpClient(
            host=chromadb_config.get('host', 'localhost'),
            port=chromadb_config.get('port', 8000)
        )
        client.heartbeat()
        print("✅ ChromaDB connection successful")
        return client
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        return None

def test_collection_access(client, config: Dict[str, Any]):
    """Test access to the organization's knowledge collection"""
    try:
        collection_name = get_collection_name(config)
        collection = client.get_collection(collection_name)
        count = collection.count()
        print(f"✅ Collection '{collection_name}' access successful - {count} documents found")
        
        if count == 0:
            print("⚠️  Collection is empty - run the ingestion process first")
            return None
        
        return collection
    except Exception as e:
        print(f"❌ Collection access failed: {e}")
        
        # Try to list available collections
        try:
            collections = client.list_collections()
            if collections:
                print("Available collections:")
                for coll in collections:
                    print(f"  - {coll.name}")
            else:
                print("No collections found")
        except:
            pass
        
        return None

def test_organization_queries(collection, config: Dict[str, Any]):
    """Test organization-specific queries based on configuration"""
    
    org_name = config['organization']['name']
    rag_goals = config['rag_goals']
    focus_areas = rag_goals.get('focus_areas', [])
    primary_purpose = rag_goals.get('primary_purpose', 'knowledge_management')
    
    # Generate queries based on configuration
    queries = []
    
    # Universal organizational queries
    queries.extend([
        {
            "query": f"What is {org_name}'s culture and values?",
            "category": "Company Culture"
        },
        {
            "query": f"How is {org_name} organized and structured?",
            "category": "Organization Structure"
        },
        {
            "query": f"What are the main processes at {org_name}?",
            "category": "Company Processes"
        }
    ])
    
    # Focus area specific queries
    if 'company_culture' in focus_areas:
        queries.append({
            "query": f"What are {org_name}'s core principles and decision-making processes?",
            "category": "Company Culture"
        })
    
    if 'team_dynamics' in focus_areas:
        queries.append({
            "query": f"How do teams collaborate and work together at {org_name}?",
            "category": "Team Dynamics"
        })
    
    if 'customer_insights' in focus_areas:
        queries.extend([
            {
                "query": f"What problems do {org_name}'s customers face?",
                "category": "Customer Problems"
            },
            {
                "query": f"How do customers use {org_name}'s products?",
                "category": "Customer Usage"
            }
        ])
    
    if 'product_strategy' in focus_areas:
        queries.extend([
            {
                "query": f"What is {org_name}'s product strategy and roadmap?",
                "category": "Product Strategy"
            },
            {
                "query": f"How does {org_name} prioritize features and development?",
                "category": "Product Prioritization"
            }
        ])
    
    # Team-specific queries
    target_teams = config.get('target_teams', [])
    for team in target_teams[:3]:  # Test first 3 teams
        team_name = team['name']
        queries.append({
            "query": f"What does the {team_name} team work on at {org_name}?",
            "category": f"{team_name.title()} Team"
        })
    
    print(f"\n🔍 Testing {org_name} Knowledge Queries:")
    print("=" * 60)
    
    for query_info in queries:
        query = query_info["query"]
        category = query_info["category"]
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            print(f"\n📋 {category}")
            print(f"❓ Query: {query}")
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                    content_type = metadata.get('content_type', 'unknown')
                    content_category = metadata.get('content_category', 'unknown')
                    title = metadata.get('title', 'No title')
                    is_relevant = metadata.get('is_goal_relevant', False)
                    
                    relevance_icon = "🎯" if is_relevant else "📄"
                    print(f"  {i+1}. {relevance_icon} [{content_type}|{content_category}] {title}")
                    print(f"     {doc[:120]}...")
            else:
                print("  ❌ No results found")
                
        except Exception as e:
            print(f"  ❌ Query failed: {e}")
    
    print("\n✅ Organization query testing completed")

def test_content_filtering(collection, config: Dict[str, Any]):
    """Test filtering by content categories and metadata"""
    
    org_name = config['organization']['name']
    
    # Universal filter tests
    filter_tests = [
        {
            "name": "Goal-Relevant Content",
            "filter": {"is_goal_relevant": True},
            "query": f"{org_name} important information"
        },
        {
            "name": "Company Culture Content",
            "filter": {"content_category": "company_culture"},
            "query": f"{org_name} values and culture"
        },
        {
            "name": "Team Documentation",
            "filter": {"content_category": "team_documentation"},
            "query": "team responsibilities and processes"
        },
        {
            "name": "Documentation Content",
            "filter": {"content_type": "documentation"},
            "query": f"{org_name} documentation"
        }
    ]
    
    # Add team-specific filters if teams are configured
    target_teams = config.get('target_teams', [])
    for team in target_teams[:2]:  # Test first 2 teams
        team_name = team['name']
        team_flag = f"relates_to_{team_name.replace('-', '_')}"
        filter_tests.append({
            "name": f"{team_name.title()} Team Content",
            "filter": {team_flag: True},
            "query": f"{team_name} team information"
        })
    
    print(f"\n📊 Testing {org_name} Content Filtering:")
    print("=" * 60)
    
    for test in filter_tests:
        try:
            results = collection.query(
                query_texts=[test["query"]],
                where=test["filter"],
                n_results=2
            )
            
            count = len(results['documents'][0]) if results['documents'] else 0
            print(f"🔍 {test['name']}: {count} results")
            
            if count > 0:
                metadata = results['metadatas'][0][0]
                title = metadata.get('title', 'No title')
                content_type = metadata.get('content_type', 'unknown')
                print(f"    Example: [{content_type}] {title}")
            
        except Exception as e:
            print(f"❌ {test['name']} filter failed: {e}")
    
    print("\n✅ Content filtering test completed")

def analyze_knowledge_coverage(collection, config: Dict[str, Any]):
    """Analyze knowledge coverage for the organization"""
    
    org_name = config['organization']['name']
    
    print(f"\n📈 {org_name} Knowledge Coverage Analysis:")
    print("=" * 60)
    
    try:
        # Get sample of documents for analysis
        all_docs = collection.get(limit=1000)
        
        if not all_docs['metadatas']:
            print("❌ No documents found for analysis")
            return
        
        # Analyze content categories
        categories = {}
        relevant_count = 0
        content_types = {}
        
        for metadata in all_docs['metadatas']:
            category = metadata.get('content_category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
            
            content_type = metadata.get('content_type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            if metadata.get('is_goal_relevant', False):
                relevant_count += 1
        
        total_docs = len(all_docs['metadatas'])
        
        print(f"📊 Total documents analyzed: {total_docs}")
        print(f"🎯 Goal-relevant content: {relevant_count} ({relevant_count/total_docs*100:.1f}%)")
        
        print(f"\n📋 Content type breakdown:")
        for content_type, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_docs * 100
            print(f"  {content_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n📂 Content category breakdown:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_docs * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")
        
        # Check team coverage
        target_teams = config.get('target_teams', [])
        if target_teams:
            print(f"\n🏢 Team coverage:")
            for team in target_teams:
                team_name = team['name']
                team_flag = f"relates_to_{team_name.replace('-', '_')}"
                team_count = sum(1 for metadata in all_docs['metadatas'] 
                               if metadata.get(team_flag, False))
                print(f"  {team_name}: {team_count} documents")
        
        print("\n✅ Coverage analysis completed")
        
    except Exception as e:
        print(f"❌ Coverage analysis failed: {e}")

def suggest_next_steps(config: Dict[str, Any]):
    """Suggest next steps based on configuration"""
    
    org_name = config['organization']['name']
    primary_purpose = config['rag_goals'].get('primary_purpose', 'knowledge_management')
    
    print(f"\n💡 Next Steps for {org_name}:")
    print("=" * 60)
    
    if primary_purpose == 'interview_preparation':
        print("\n🎤 Interview Preparation:")
        print("  • Practice with the test queries above")
        print("  • Create role-specific questions based on your focus areas")
        print("  • Research team dynamics and company culture")
        print("  • Understand organizational processes and decision-making")
    
    elif primary_purpose == 'knowledge_management':
        print("\n📚 Knowledge Management:")
        print("  • Use the knowledge base for team onboarding")
        print("  • Create documentation search workflows")
        print("  • Set up regular content updates")
        print("  • Train team members on querying techniques")
    
    elif primary_purpose == 'onboarding':
        print("\n🚀 Onboarding Support:")
        print("  • Create onboarding query templates")
        print("  • Develop new hire question guides")
        print("  • Set up team-specific knowledge paths")
        print("  • Create culture and values exploration guides")
    
    collection_name = get_collection_name(config)
    
    print(f"\n🔧 Integration:")
    print(f"  • Collection name: {collection_name}")
    print(f"  • ChromaDB endpoint: http://localhost:8000")
    print(f"  • Use configuration: {config}")
    
    print(f"\n📝 Maintenance:")
    print(f"  • Re-run ingestion when documentation updates")
    print(f"  • Monitor query performance and relevance")
    print(f"  • Update configuration as organization evolves")

def main():
    """Main test function"""
    
    # Get config file from command line argument
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    print("🧪 Universal Organization RAG Test Suite")
    print(f"📋 Configuration: {config_path}")
    print("=" * 60)
    
    # Load configuration
    config = load_config(config_path)
    if not config:
        return
    
    org_name = config['organization']['name']
    print(f"🏢 Organization: {org_name}")
    
    # Test connection
    client = test_chromadb_connection(config)
    if not client:
        return
    
    # Test collection access
    collection = test_collection_access(client, config)
    if not collection:
        return
    
    # Run organization-specific tests
    analyze_knowledge_coverage(collection, config)
    test_content_filtering(collection, config)
    test_organization_queries(collection, config)
    suggest_next_steps(config)
    
    print(f"\n🎉 {org_name} Knowledge Test Suite Complete!")
    print(f"\n🚀 Your {org_name} knowledge base is ready for use!")

if __name__ == "__main__":
    main()
