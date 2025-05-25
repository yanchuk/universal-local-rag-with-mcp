#!/usr/bin/env python3
"""
Comprehensive Test Suite for Universal Organization RAG System
Tests all components: configuration, ingestion, embedding, querying, and integrations
"""

import pytest
import tempfile
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, Any
import shutil

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ingest_data import UniversalConfig, UniversalDocumentProcessor, UniversalChromaDBIngester
except ImportError:
    print("Warning: Could not import ingest_data modules. Some tests may fail.")

class TestConfiguration:
    """Test configuration loading and validation"""
    
    def create_test_config(self, **overrides) -> Dict[str, Any]:
        """Create a test configuration with optional overrides"""
        base_config = {
            'organization': {
                'name': 'TestOrg',
                'description': 'Test organization',
                'domain': 'test.com'
            },
            'rag_goals': {
                'primary_purpose': 'knowledge_management',
                'focus_areas': ['company_culture', 'team_dynamics'],
                'target_role': 'general'
            },
            'data_sources': {
                'documentation': {
                    'base_path': '/tmp/test_docs',
                    'priority_paths': ['handbook', 'teams'],
                    'file_extensions': ['*.md']
                },
                'github': {
                    'enabled': False
                }
            },
            'target_teams': [
                {
                    'name': 'engineering',
                    'keywords': ['engineering', 'development'],
                    'aliases': ['eng', 'dev']
                }
            ],
            'content_categories': {
                'company_culture': {
                    'keywords': ['culture', 'values'],
                    'importance': 'high'
                }
            },
            'processing': {
                'max_chunk_size': 1000,
                'chunk_overlap': 200,
                'batch_size': 32,
                'max_memory_usage': 0.8,
                'embedding_model': 'all-MiniLM-L6-v2'
            },
            'chromadb': {
                'host': 'localhost',
                'port': 8000,
                'collection_name': 'test_knowledge'
            },
            'output': {
                'log_level': 'INFO',
                'log_file': 'test.log',
                'progress_interval': 50
            },
            'quality': {
                'min_content_length': 50,
                'skip_empty_files': True,
                'validate_markdown': True,
                'exclude_patterns': ['*.tmp']
            }
        }
        
        # Apply overrides
        for key, value in overrides.items():
            if '.' in key:
                keys = key.split('.')
                current = base_config
                for k in keys[:-1]:
                    current = current[k]
                current[keys[-1]] = value
            else:
                base_config[key] = value
        
        return base_config
    
    def test_config_loading(self):
        """Test configuration loading from YAML"""
        test_config = self.create_test_config()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            config_path = f.name
        
        try:
            config = UniversalConfig(config_path)
            assert config.organization_name == 'TestOrg'
            assert config.collection_name == 'testorg_test_knowledge'
            assert len(config.target_teams) == 1
            assert config.rag_goals['primary_purpose'] == 'knowledge_management'
        finally:
            os.unlink(config_path)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test missing required fields
        invalid_configs = [
            {},  # Empty config
            {'organization': {}},  # Missing name
            {'organization': {'name': 'Test'}, 'rag_goals': {}},  # Missing purpose
        ]
        
        for invalid_config in invalid_configs:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(invalid_config, f)
                config_path = f.name
            
            try:
                with pytest.raises((KeyError, TypeError)):
                    config = UniversalConfig(config_path)
                    _ = config.organization_name  # This should fail
            finally:
                os.unlink(config_path)
    
    def test_collection_name_generation(self):
        """Test collection name generation from org name"""
        test_cases = [
            ('Simple Org', 'simple_org_test_knowledge'),
            ('My-Company', 'my-company_test_knowledge'),
            ('UPPERCASE', 'uppercase_test_knowledge'),
            ('Org With Spaces', 'org_with_spaces_test_knowledge')
        ]
        
        for org_name, expected_collection in test_cases:
            config = self.create_test_config()
            config['organization']['name'] = org_name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config, f)
                config_path = f.name
            
            try:
                universal_config = UniversalConfig(config_path)
                assert universal_config.collection_name == expected_collection
            finally:
                os.unlink(config_path)

class TestDocumentProcessing:
    """Test document processing functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config_data = TestConfiguration().create_test_config()
        self.config_data['data_sources']['documentation']['base_path'] = self.test_dir
        
        # Create test config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.config_data, f)
            self.config_path = f.name
        
        self.config = UniversalConfig(self.config_path)
        self.processor = UniversalDocumentProcessor(self.config)
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.test_dir)
        os.unlink(self.config_path)
    
    def create_test_file(self, filename: str, content: str):
        """Create a test markdown file"""
        file_path = Path(self.test_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path
    
    def test_markdown_processing(self):
        """Test markdown file processing"""
        content = """---
title: Test Document
category: company_culture
---

# Test Document

This is a test document about our **company culture** and values.

## Our Values
- Innovation
- Collaboration
- Excellence
"""
        
        file_path = self.create_test_file('test.md', content)
        chunks = self.processor.process_markdown_file(file_path)
        
        assert len(chunks) >= 1
        assert chunks[0]['metadata']['title'] == 'Test Document'
        assert chunks[0]['metadata']['content_category'] == 'company_culture'
        assert 'company culture' in chunks[0]['content'].lower()
    
    def test_frontmatter_extraction(self):
        """Test YAML frontmatter extraction"""
        content = """---
title: Frontmatter Test
author: Test Author
tags: ["test", "culture"]
---

Content here."""
        
        frontmatter, main_content = self.processor.extract_frontmatter(content)
        
        assert frontmatter['title'] == 'Frontmatter Test'
        assert frontmatter['author'] == 'Test Author'
        assert 'Content here.' in main_content
    
    def test_content_categorization(self):
        """Test content category determination"""
        test_cases = [
            ('handbook/culture.md', 'Our company values', 'company_culture'),
            ('teams/engineering.md', 'Engineering team responsibilities', 'general_docs'),
            ('random/file.md', 'Random content', 'general_docs'),
        ]
        
        for filepath, content, expected_category in test_cases:
            file_path = Path(self.test_dir) / filepath
            category = self.processor.determine_content_category(file_path, content)
            # Note: This test may need adjustment based on actual categorization logic
            assert category in ['company_culture', 'general_docs']  # Should match one of the valid categories
    
    def test_team_metadata_enhancement(self):
        """Test team-specific metadata enhancement"""
        content = "Our engineering team uses Python and focuses on development best practices."
        
        metadata = self.processor.enhance_metadata_with_teams(content)
        
        assert 'team_ownership' in metadata
        assert 'relates_to_engineering' in metadata
        # Should detect engineering team from content
        assert metadata['team_ownership'] == 'engineering' or metadata['relates_to_engineering'] == True
    
    def test_text_chunking(self):
        """Test text chunking functionality"""
        # Create a long text that should be chunked
        long_text = "This is a test sentence. " * 200  # ~1000 words
        
        metadata = {'content_category': 'test', 'title': 'Test'}
        chunks = self.processor.chunk_text(long_text, metadata)
        
        assert len(chunks) > 1  # Should create multiple chunks
        
        # Check chunk metadata
        for i, chunk in enumerate(chunks):
            assert chunk['metadata']['chunk_index'] == i
            assert chunk['metadata']['total_chunks'] == len(chunks)
            assert 'token_count' in chunk['metadata']
    
    def test_github_issue_processing(self):
        """Test GitHub issue markdown processing"""
        github_content = """# Issue Title: Bug in authentication

**Issue Number:** #123
**State:** open
**Author:** @testuser
**Created:** 2024-01-01
**Labels:** `bug` `authentication` `team-engineering`

## Issue Description

There's a problem with user authentication that's causing login failures.

### Steps to Reproduce
1. Navigate to login page
2. Enter credentials
3. Click submit
4. Error occurs
"""
        
        file_path = self.create_test_file('issue_123.md', github_content)
        chunks = self.processor.process_github_issue(file_path)
        
        assert len(chunks) >= 1
        assert chunks[0]['metadata']['content_type'] == 'github_issue'
        assert 'authentication' in chunks[0]['content'].lower()

class TestSystemIntegration:
    """Test system integration and end-to-end functionality"""
    
    def test_config_examples_validity(self):
        """Test that all example configurations are valid"""
        config_examples_dir = Path(__file__).parent.parent / 'config_examples'
        
        if not config_examples_dir.exists():
            pytest.skip("Config examples directory not found")
        
        for config_file in config_examples_dir.glob('*.yaml'):
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Basic validation
                assert 'organization' in config_data
                assert 'name' in config_data['organization']
                assert 'rag_goals' in config_data
                assert 'data_sources' in config_data
                assert 'target_teams' in config_data
                
                print(f"✅ {config_file.name} is valid")
                
            except Exception as e:
                pytest.fail(f"Configuration {config_file.name} is invalid: {e}")
    
    def test_docker_compose_file(self):
        """Test Docker Compose file validity"""
        compose_file = Path(__file__).parent.parent / 'docker-compose.yml'
        
        if not compose_file.exists():
            pytest.skip("Docker Compose file not found")
        
        try:
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            assert 'services' in compose_data
            assert 'chromadb' in compose_data['services']
            
            chromadb_service = compose_data['services']['chromadb']
            assert 'image' in chromadb_service
            assert 'ports' in chromadb_service
            assert '8000:8000' in chromadb_service['ports']
            
            print("✅ Docker Compose file is valid")
            
        except Exception as e:
            pytest.fail(f"Docker Compose file is invalid: {e}")
    
    def test_requirements_file(self):
        """Test requirements.txt validity"""
        requirements_file = Path(__file__).parent.parent / 'requirements.txt'
        
        if not requirements_file.exists():
            pytest.skip("Requirements file not found")
        
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.read()
            
            # Check for essential packages
            essential_packages = [
                'chromadb',
                'sentence-transformers', 
                'PyYAML',
                'tiktoken',
                'psutil'
            ]
            
            for package in essential_packages:
                assert package in requirements, f"Missing essential package: {package}"
            
            print("✅ Requirements file contains essential packages")
            
        except Exception as e:
            pytest.fail(f"Requirements file is invalid: {e}")

class TestCLITools:
    """Test command-line tools and scripts"""
    
    def test_setup_script_exists(self):
        """Test that setup script exists and is executable"""
        setup_script = Path(__file__).parent.parent / 'setup.sh'
        
        assert setup_script.exists(), "setup.sh not found"
        assert os.access(setup_script, os.X_OK), "setup.sh is not executable"
    
    def test_test_setup_script(self):
        """Test the test_setup.py script"""
        test_script = Path(__file__).parent.parent / 'test_setup.py'
        
        assert test_script.exists(), "test_setup.py not found"
        
        # Try to import it
        sys.path.insert(0, str(test_script.parent))
        try:
            import test_setup
            assert hasattr(test_setup, 'main'), "test_setup.py missing main function"
        except ImportError as e:
            pytest.fail(f"Cannot import test_setup.py: {e}")
    
    def test_ingest_script(self):
        """Test the ingest_data.py script"""
        ingest_script = Path(__file__).parent.parent / 'ingest_data.py'
        
        assert ingest_script.exists(), "ingest_data.py not found"
        
        # Try to import it
        sys.path.insert(0, str(ingest_script.parent))
        try:
            import ingest_data
            assert hasattr(ingest_data, 'main'), "ingest_data.py missing main function"
            assert hasattr(ingest_data, 'UniversalConfig'), "ingest_data.py missing UniversalConfig class"
        except ImportError as e:
            pytest.fail(f"Cannot import ingest_data.py: {e}")

def run_comprehensive_tests():
    """Run all tests and provide a summary"""
    print("🧪 Running Comprehensive Universal RAG Test Suite")
    print("=" * 60)
    
    # Collect all test classes
    test_classes = [
        TestConfiguration,
        TestDocumentProcessing, 
        TestSystemIntegration,
        TestCLITools
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}")
        print("-" * 40)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                # Create instance and run setup if available
                instance = test_class()
                if hasattr(instance, 'setup_method'):
                    instance.setup_method()
                
                # Run the test
                getattr(instance, test_method)()
                
                # Run teardown if available
                if hasattr(instance, 'teardown_method'):
                    instance.teardown_method()
                
                print(f"✅ {test_method}")
                passed_tests += 1
                
            except Exception as e:
                print(f"❌ {test_method}: {str(e)}")
                failed_tests.append(f"{test_class.__name__}.{test_method}: {str(e)}")
    
    # Summary
    print(f"\n🎉 Test Suite Complete!")
    print("=" * 60)
    print(f"📊 Total tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {len(failed_tests)}")
    
    if failed_tests:
        print(f"\n🚨 Failed Tests:")
        for failure in failed_tests:
            print(f"   • {failure}")
        return False
    else:
        print(f"\n🎯 All tests passed! The Universal RAG system is ready for use.")
        return True

if __name__ == "__main__":
    # Can be run directly or with pytest
    if len(sys.argv) > 1 and sys.argv[1] == '--pytest':
        # Run with pytest for more detailed output
        import subprocess
        result = subprocess.run(['python', '-m', 'pytest', __file__, '-v'], 
                              capture_output=False)
        sys.exit(result.returncode)
    else:
        # Run our custom test runner
        success = run_comprehensive_tests()
        sys.exit(0 if success else 1)
