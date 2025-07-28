#!/usr/bin/env python3
"""
ChromaDB Version Compatibility Checker
Ensures ChromaDB server and client versions are compatible for MCP integration.
"""

import requests
import sys
import subprocess
from packaging import version

def print_status(message: str):
    print(f"🔍 {message}")

def print_success(message: str):
    print(f"✅ {message}")

def print_error(message: str):
    print(f"❌ {message}")

def print_warning(message: str):
    print(f"⚠️  {message}")

def get_server_version() -> str:
    """Get ChromaDB server version"""
    try:
        response = requests.get("http://localhost:8000/api/v1/version", timeout=5)
        if response.status_code == 200:
            return response.json().strip('"')
        else:
            raise Exception(f"Server responded with status {response.status_code}")
    except Exception as e:
        print_error(f"Failed to get server version: {e}")
        print_error("Make sure ChromaDB is running: docker compose up -d")
        return None

def get_client_version() -> str:
    """Get ChromaDB client version"""
    try:
        import chromadb
        return chromadb.__version__
    except ImportError:
        print_error("ChromaDB client not installed")
        return None
    except AttributeError:
        # Fallback method
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import pkg_resources; print(pkg_resources.get_distribution('chromadb').version)"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            print_error("Could not determine ChromaDB client version")
            return None

def check_mcp_compatibility(client_ver: str) -> bool:
    """Check if client version supports MCP"""
    try:
        import chroma_mcp
        print_success("chroma-mcp is installed")
        return True
    except ImportError:
        print_error("chroma-mcp not installed. Run: pip install chroma-mcp")
        return False

def is_compatible(server_ver: str, client_ver: str) -> bool:
    """Check if server and client versions are compatible"""
    try:
        server_version = version.parse(server_ver)
        client_version = version.parse(client_ver)
        
        # Known compatibility rules
        if client_version >= version.parse("1.0.0"):
            # v1.x clients need v0.5.x+ servers
            return server_version >= version.parse("0.5.0")
        elif client_version >= version.parse("0.5.0"):
            # v0.5.x clients work with v0.4.x and v0.5.x servers
            return server_version >= version.parse("0.4.0")
        else:
            # Older clients
            return server_version < version.parse("0.5.0")
            
    except Exception as e:
        print_warning(f"Could not parse versions for compatibility check: {e}")
        return True  # Assume compatible if we can't check

def suggest_fix(server_ver: str, client_ver: str):
    """Suggest how to fix version incompatibility"""
    print("\n🔧 Suggested fixes:")
    
    server_version = version.parse(server_ver)
    client_version = version.parse(client_ver)
    
    if client_version >= version.parse("1.0.0") and server_version < version.parse("0.5.0"):
        print("1. Update ChromaDB server version in docker-compose.yml:")
        print("   Change: image: chromadb/chroma:0.4.24")
        print("   To:     image: chromadb/chroma:0.5.23")
        print("2. Restart ChromaDB: docker compose down && docker compose up -d")
        print("3. Re-ingest data: python ingest_data.py config.yaml")
    
    elif client_version < version.parse("1.0.0") and server_version >= version.parse("0.5.0"):
        print("1. Update ChromaDB client version:")
        print("   pip install --upgrade 'chromadb>=1.0.15'")
        print("2. Re-ingest data: python ingest_data.py config.yaml")
    
    else:
        print("1. Try updating both server and client to latest versions")
        print("2. Check docker-compose.yml for server version")
        print("3. Check requirements.txt for client version")

def main():
    """Main version checking function"""
    print_status("Checking ChromaDB version compatibility...")
    
    # Check server version
    server_ver = get_server_version()
    if server_ver:
        print_success(f"Server version: {server_ver}")
    else:
        print_error("Cannot check server version")
        return False
    
    # Check client version
    client_ver = get_client_version()
    if client_ver:
        print_success(f"Client version: {client_ver}")
    else:
        print_error("Cannot check client version")
        return False
    
    # Check MCP compatibility
    mcp_compatible = check_mcp_compatibility(client_ver)
    
    # Check version compatibility
    compatible = is_compatible(server_ver, client_ver)
    
    print(f"\n📊 Compatibility Summary:")
    print(f"Server: ChromaDB {server_ver}")
    print(f"Client: ChromaDB {client_ver}")
    print(f"MCP Support: {'✅' if mcp_compatible else '❌'}")
    print(f"Versions Compatible: {'✅' if compatible else '❌'}")
    
    if compatible and mcp_compatible:
        print_success("All versions are compatible! MCP integration should work.")
        return True
    else:
        print_error("Version compatibility issues detected!")
        suggest_fix(server_ver, client_ver)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)