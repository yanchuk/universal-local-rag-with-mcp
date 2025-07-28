#!/usr/bin/env python3
"""
MCP Setup Automation Script
Automates Claude Desktop MCP configuration based on findings from troubleshooting.
"""

import json
import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Any

def print_status(message: str):
    print(f"🔧 {message}")

def print_success(message: str):
    print(f"✅ {message}")

def print_error(message: str):
    print(f"❌ {message}")

def get_claude_config_path() -> Path:
    """Get Claude Desktop config file path based on OS"""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        return Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config/claude/claude_desktop_config.json"

def get_venv_chroma_mcp_path() -> str:
    """Get the full path to chroma-mcp in the virtual environment"""
    try:
        result = subprocess.run(
            ["which", "chroma-mcp"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print_error("chroma-mcp not found. Make sure virtual environment is activated and chroma-mcp is installed.")
        sys.exit(1)

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load RAG configuration"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print_error(f"Failed to load config: {e}")
        sys.exit(1)

def get_collection_name(config: Dict[str, Any]) -> str:
    """Get collection name from config"""
    org_name = config['organization']['name'].lower().replace(' ', '_').replace('-', '_')
    base_name = config['chromadb']['collection_name']
    return f"{org_name}_{base_name}"

def create_mcp_config(chroma_mcp_path: str, collection_name: str) -> Dict[str, Any]:
    """Create MCP configuration for Claude Desktop"""
    return {
        "mcpServers": {
            f"{collection_name.split('_')[0]}_knowledge": {
                "command": chroma_mcp_path,
                "args": [
                    "--client-type", "http",
                    "--host", "localhost",
                    "--port", "8000",
                    "--ssl", "false"
                ]
            }
        }
    }

def update_claude_config(claude_config_path: Path, mcp_config: Dict[str, Any]):
    """Update Claude Desktop configuration"""
    existing_config = {}
    
    # Load existing config if it exists
    if claude_config_path.exists():
        try:
            with open(claude_config_path, 'r') as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            print_error(f"Invalid JSON in {claude_config_path}. Please fix manually.")
            return False
    
    # Merge MCP servers
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"].update(mcp_config["mcpServers"])
    
    # Ensure directory exists
    claude_config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write updated config
    try:
        with open(claude_config_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
        return True
    except Exception as e:
        print_error(f"Failed to write Claude config: {e}")
        return False

def verify_setup():
    """Verify that the setup is correct"""
    print_status("Verifying setup...")
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_error("Virtual environment not activated. Run 'source venv/bin/activate' first.")
        return False
    
    # Check if ChromaDB is running
    try:
        import requests
        response = requests.get("http://localhost:8000/api/v1/heartbeat", timeout=5)
        if response.status_code == 200:
            print_success("ChromaDB is running")
        else:
            print_error("ChromaDB is not responding correctly")
            return False
    except Exception:
        print_error("ChromaDB is not running. Start with 'docker compose up -d'")
        return False
    
    # Check if chroma-mcp is installed
    try:
        import chroma_mcp
        print_success("chroma-mcp is installed")
    except ImportError:
        print_error("chroma-mcp not installed. Run 'pip install chroma-mcp'")
        return False
    
    return True

def main():
    """Main setup function"""
    print_status("Setting up Claude Desktop MCP integration...")
    
    # Verify setup prerequisites
    if not verify_setup():
        sys.exit(1)
    
    # Load RAG configuration
    config = load_config()
    collection_name = get_collection_name(config)
    print_success(f"Collection name: {collection_name}")
    
    # Get chroma-mcp path
    chroma_mcp_path = get_venv_chroma_mcp_path()
    print_success(f"chroma-mcp path: {chroma_mcp_path}")
    
    # Create MCP configuration
    mcp_config = create_mcp_config(chroma_mcp_path, collection_name)
    
    # Get Claude config path
    claude_config_path = get_claude_config_path()
    print_status(f"Claude config path: {claude_config_path}")
    
    # Update Claude configuration
    if update_claude_config(claude_config_path, mcp_config):
        print_success("Claude Desktop configuration updated!")
        
        print("\n🎉 MCP Setup Complete!")
        print("\nNext steps:")
        print("1. Restart Claude Desktop completely")
        print("2. Test with queries like:")
        print("   - 'List available tools'")
        print("   - 'Search for company culture'")
        print(f"   - 'Query the {collection_name.split('_')[0]} knowledge base'")
        
        # Display the configuration for verification
        print(f"\n📋 Configuration added to {claude_config_path}:")
        print(json.dumps(mcp_config, indent=2))
        
    else:
        print_error("Failed to update Claude Desktop configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()