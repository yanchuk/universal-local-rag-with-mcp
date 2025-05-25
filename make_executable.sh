#!/bin/bash

# Make Scripts Executable
# This script makes all necessary scripts executable for the Universal RAG system

echo "🔧 Making Universal RAG scripts executable..."

# Make shell scripts executable
chmod +x setup.sh
chmod +x scripts/test_docker.sh

# Make Python scripts executable
chmod +x ingest_data.py
chmod +x test_setup.py
chmod +x scripts/interview_prep.py
chmod +x scripts/manage.py
chmod +x scripts/test_comprehensive.py

echo "✅ All scripts are now executable"

# List what was made executable
echo ""
echo "📋 Executable files:"
echo "  • setup.sh - Main setup script"
echo "  • ingest_data.py - Data ingestion engine"
echo "  • test_setup.py - System testing"
echo "  • scripts/test_docker.sh - Docker compatibility test"
echo "  • scripts/interview_prep.py - Interview preparation tool"
echo "  • scripts/manage.py - System management CLI"
echo "  • scripts/test_comprehensive.py - Comprehensive test suite"

echo ""
echo "🚀 Ready to use! Run './setup.sh' to get started."
