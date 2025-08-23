#!/usr/bin/env python3
"""
Smart Manifest Updater
Updates manifests incrementally while preserving manual additions
"""

import os
import json
import yaml
import subprocess
from pathlib import Path
from datetime import datetime
import hashlib
import argparse

class SmartManifestUpdater:
    def __init__(self, project_path=None):
        self.project_path = Path(project_path or os.getcwd())
        self.manifest_dir = self.project_path / '.claude' / 'manifests'
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        
    def update_all(self, incremental=True, preserve_manual=True):
        """Update all manifests intelligently"""
        manifests = [
            'project-manifest.json',
            'api-manifest.json',
            'database-manifest.json',
            'component-manifest.json',
            'test-manifest.json',
            'security-manifest.json',
            'deployment-manifest.json',
            'dependencies-manifest.json'
        ]
        
        results = {}
        for manifest_name in manifests:
            result = self.update_manifest(manifest_name, incremental, preserve_manual)
            results[manifest_name] = result
        
        return results
    
    def update_manifest(self, manifest_name, incremental=True, preserve_manual=True):
        """Update a single manifest"""
        manifest_path = self.manifest_dir / manifest_name
        manifest_type = manifest_name.split('-')[0]
        
        # Load existing manifest if it exists
        existing = {}
        if manifest_path.exists():
            with open(manifest_path) as f:
                if manifest_name.endswith('.json'):
                    existing = json.load(f)
                else:
                    existing = yaml.safe_load(f)
        
        # Generate new data based on type
        new_data = self.generate_manifest_data(manifest_type)
        
        # Merge intelligently
        if incremental and existing:
            final = self.smart_merge(existing, new_data, preserve_manual)
        else:
            final = new_data
        
        # Add metadata
        final['_metadata'] = {
            'lastUpdated': datetime.now().isoformat(),
            'version': existing.get('_metadata', {}).get('version', 0) + 1,
            'updateType': 'incremental' if incremental else 'full',
            'preservedManual': preserve_manual
        }
        
        # Save manifest
        with open(manifest_path, 'w') as f:
            if manifest_name.endswith('.json'):
                json.dump(final, f, indent=2)
            else:
                yaml.dump(final, f, default_flow_style=False)
        
        return {
            'updated': True,
            'changes': self.count_changes(existing, final),
            'version': final['_metadata']['version']
        }
    
    def generate_manifest_data(self, manifest_type):
        """Generate manifest data based on type"""
        generators = {
            'project': self.generate_project_manifest,
            'api': self.generate_api_manifest,
            'database': self.generate_database_manifest,
            'component': self.generate_component_manifest,
            'test': self.generate_test_manifest,
            'security': self.generate_security_manifest,
            'deployment': self.generate_deployment_manifest,
            'dependencies': self.generate_dependencies_manifest
        }
        
        generator = generators.get(manifest_type, self.generate_generic_manifest)
        return generator()
    
    def generate_project_manifest(self):
        """Generate project structure manifest"""
        manifest = {
            'name': self.get_project_name(),
            'type': self.detect_project_type(),
            'structure': {},
            'entryPoints': [],
            'configuration': [],
            'scripts': {}
        }
        
        # Map directory structure
        for item in self.project_path.iterdir():
            if not item.name.startswith('.') and item.is_dir():
                manifest['structure'][item.name] = self.get_dir_description(item.name)
        
        # Find entry points
        entry_files = ['index.js', 'main.py', 'app.js', 'server.js']
        for entry in entry_files:
            if (self.project_path / entry).exists():
                manifest['entryPoints'].append(entry)
        
        # Find config files
        config_patterns = ['*.config.js', '*.json', '.env*']
        for pattern in config_patterns:
            for config_file in self.project_path.glob(pattern):
                if not config_file.name.startswith('.git'):
                    manifest['configuration'].append(str(config_file.relative_to(self.project_path)))
        
        # Get package.json scripts if exists
        package_file = self.project_path / 'package.json'
        if package_file.exists():
            with open(package_file) as f:
                package = json.load(f)
                manifest['scripts'] = package.get('scripts', {})
        
        return manifest
    
    def generate_api_manifest(self):
        """Generate API endpoints manifest"""
        manifest = {
            'endpoints': [],
            'graphql': {},
            'websockets': [],
            'authentication': {}
        }
        
        # Find API route files
        api_patterns = ['**/api/**/*.{js,ts,py}', '**/routes/**/*.{js,ts,py}']
        for pattern in api_patterns:
            for api_file in self.project_path.glob(pattern):
                endpoints = self.extract_endpoints(api_file)
                manifest['endpoints'].extend(endpoints)
        
        return manifest
    
    def generate_database_manifest(self):
        """Generate database manifest"""
        manifest = {
            'type': self.detect_database_type(),
            'schemas': [],
            'models': [],
            'migrations': []
        }
        
        # Find schema files
        schema_patterns = ['**/schema.{sql,prisma}', '**/models/**/*.{js,ts,py}']
        for pattern in schema_patterns:
            for schema_file in self.project_path.glob(pattern):
                manifest['schemas'].append(str(schema_file.relative_to(self.project_path)))
        
        # Find migrations
        migration_dirs = ['migrations', 'db/migrate', 'database/migrations']
        for mig_dir in migration_dirs:
            mig_path = self.project_path / mig_dir
            if mig_path.exists():
                for migration in mig_path.iterdir():
                    manifest['migrations'].append(migration.name)
        
        return manifest
    
    def generate_component_manifest(self):
        """Generate UI component manifest"""
        manifest = {
            'components': [],
            'pages': [],
            'layouts': [],
            'hooks': [],
            'utilities': []
        }
        
        # Find components
        component_patterns = [
            '**/components/**/*.{jsx,tsx,vue}',
            '**/pages/**/*.{jsx,tsx,vue}',
            '**/layouts/**/*.{jsx,tsx,vue}'
        ]
        
        for pattern in component_patterns:
            for component_file in self.project_path.glob(pattern):
                rel_path = str(component_file.relative_to(self.project_path))
                
                if 'components' in rel_path:
                    manifest['components'].append(rel_path)
                elif 'pages' in rel_path:
                    manifest['pages'].append(rel_path)
                elif 'layouts' in rel_path:
                    manifest['layouts'].append(rel_path)
        
        return manifest
    
    def generate_test_manifest(self):
        """Generate test manifest"""
        manifest = {
            'testFiles': [],
            'coverage': {},
            'commands': {}
        }
        
        # Find test files
        test_patterns = ['**/*.{spec,test}.{js,ts,jsx,tsx,py}', '**/tests/**/*', '**/__tests__/**/*']
        for pattern in test_patterns:
            for test_file in self.project_path.glob(pattern):
                if 'node_modules' not in str(test_file):
                    manifest['testFiles'].append(str(test_file.relative_to(self.project_path)))
        
        # Get test commands from package.json
        package_file = self.project_path / 'package.json'
        if package_file.exists():
            with open(package_file) as f:
                package = json.load(f)
                scripts = package.get('scripts', {})
                test_scripts = {k: v for k, v in scripts.items() if 'test' in k}
                manifest['commands'] = test_scripts
        
        # Try to get coverage
        coverage_file = self.project_path / 'coverage' / 'coverage-summary.json'
        if coverage_file.exists():
            with open(coverage_file) as f:
                manifest['coverage'] = json.load(f)
        
        return manifest
    
    def generate_security_manifest(self):
        """Generate security manifest"""
        manifest = {
            'authentication': {},
            'authorization': {},
            'encryption': [],
            'validation': [],
            'dependencies': {}
        }
        
        # Find auth files
        auth_patterns = ['**/auth/**/*.{js,ts,py}', '**/security/**/*.{js,ts,py}']
        for pattern in auth_patterns:
            for auth_file in self.project_path.glob(pattern):
                rel_path = str(auth_file.relative_to(self.project_path))
                if 'auth' in rel_path.lower():
                    manifest['authentication'][rel_path] = 'Found'
        
        return manifest
    
    def generate_deployment_manifest(self):
        """Generate deployment manifest"""
        manifest = {
            'environments': [],
            'cicd': {},
            'docker': {},
            'infrastructure': {}
        }
        
        # Check for CI/CD configs
        cicd_files = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', '.circleci']
        for cicd in cicd_files:
            cicd_path = self.project_path / cicd
            if cicd_path.exists():
                manifest['cicd'][cicd] = 'Present'
        
        # Check for Docker
        docker_files = ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']
        for docker in docker_files:
            docker_path = self.project_path / docker
            if docker_path.exists():
                manifest['docker'][docker] = 'Present'
        
        return manifest
    
    def generate_dependencies_manifest(self):
        """Generate dependencies manifest"""
        manifest = {
            'production': {},
            'development': {},
            'outdated': [],
            'vulnerabilities': []
        }
        
        # Check package.json
        package_file = self.project_path / 'package.json'
        if package_file.exists():
            with open(package_file) as f:
                package = json.load(f)
                manifest['production'] = package.get('dependencies', {})
                manifest['development'] = package.get('devDependencies', {})
        
        # Check for requirements.txt
        requirements_file = self.project_path / 'requirements.txt'
        if requirements_file.exists():
            with open(requirements_file) as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                manifest['production']['python'] = deps
        
        return manifest
    
    def generate_generic_manifest(self):
        """Generate generic manifest"""
        return {
            'files': [],
            'directories': [],
            'metadata': {}
        }
    
    def smart_merge(self, existing, new_data, preserve_manual=True):
        """Intelligently merge existing and new manifest data"""
        merged = existing.copy()
        
        # Preserve manual sections
        if preserve_manual and '_manual' in existing:
            merged['_manual'] = existing['_manual']
        
        # Update auto-generated sections
        for key, value in new_data.items():
            if key.startswith('_manual'):
                continue  # Skip manual sections
            
            if isinstance(value, dict) and key in existing and isinstance(existing[key], dict):
                # Merge dictionaries
                merged[key] = self.merge_dicts(existing[key], value)
            elif isinstance(value, list) and key in existing and isinstance(existing[key], list):
                # Merge lists (union)
                merged[key] = list(set(existing[key] + value))
            else:
                # Replace value
                merged[key] = value
        
        return merged
    
    def merge_dicts(self, dict1, dict2):
        """Recursively merge two dictionaries"""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
    
    def count_changes(self, old, new):
        """Count changes between manifests"""
        # Simple change counter - could be more sophisticated
        old_json = json.dumps(old, sort_keys=True)
        new_json = json.dumps(new, sort_keys=True)
        
        if old_json == new_json:
            return 0
        
        # Count different keys
        old_keys = set(self.flatten_keys(old))
        new_keys = set(self.flatten_keys(new))
        
        added = len(new_keys - old_keys)
        removed = len(old_keys - new_keys)
        
        return added + removed
    
    def flatten_keys(self, d, parent_key=''):
        """Flatten dictionary keys for comparison"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_keys(v, new_key))
            else:
                items.append(new_key)
        return items
    
    def extract_endpoints(self, file_path):
        """Extract API endpoints from file"""
        endpoints = []
        try:
            with open(file_path) as f:
                content = f.read()
                
                # Simple pattern matching for common API patterns
                import re
                patterns = [
                    r"app\.(get|post|put|delete|patch)\(['\"]([^'\"]+)",
                    r"router\.(get|post|put|delete|patch)\(['\"]([^'\"]+)",
                    r"@(Get|Post|Put|Delete|Patch)\(['\"]([^'\"]+)"
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        method, path = match
                        endpoints.append({
                            'method': method.upper(),
                            'path': path,
                            'file': str(file_path.relative_to(self.project_path))
                        })
        except Exception:
            pass
        
        return endpoints
    
    def detect_project_type(self):
        """Detect project type"""
        if (self.project_path / 'package.json').exists():
            return 'JavaScript/TypeScript'
        elif (self.project_path / 'requirements.txt').exists():
            return 'Python'
        elif (self.project_path / 'go.mod').exists():
            return 'Go'
        else:
            return 'Unknown'
    
    def detect_database_type(self):
        """Detect database type"""
        if (self.project_path / 'prisma').exists():
            return 'PostgreSQL/Prisma'
        elif (self.project_path / 'migrations').exists():
            return 'SQL'
        else:
            return 'Unknown'
    
    def get_project_name(self):
        """Get project name"""
        package_file = self.project_path / 'package.json'
        if package_file.exists():
            with open(package_file) as f:
                return json.load(f).get('name', self.project_path.name)
        return self.project_path.name
    
    def get_dir_description(self, dir_name):
        """Get description for directory"""
        descriptions = {
            'src': 'Source code',
            'tests': 'Test files',
            'docs': 'Documentation',
            'public': 'Public assets',
            'config': 'Configuration files',
            'scripts': 'Build and utility scripts',
            'lib': 'Library code',
            'api': 'API endpoints',
            'components': 'UI components',
            'pages': 'Page components',
            'utils': 'Utility functions',
            'services': 'Service layer',
            'models': 'Data models',
            'controllers': 'Controllers',
            'middleware': 'Middleware',
            'database': 'Database files',
            'migrations': 'Database migrations'
        }
        return descriptions.get(dir_name, f'{dir_name} directory')

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Smart Manifest Updater')
    parser.add_argument('--path', default='.', help='Project path')
    parser.add_argument('--incremental', action='store_true', help='Incremental update')
    parser.add_argument('--preserve-manual', action='store_true', help='Preserve manual sections')
    parser.add_argument('--manifest', help='Update specific manifest')
    
    args = parser.parse_args()
    
    updater = SmartManifestUpdater(args.path)
    
    if args.manifest:
        result = updater.update_manifest(args.manifest, args.incremental, args.preserve_manual)
        print(f"Updated {args.manifest}: {result}")
    else:
        results = updater.update_all(args.incremental, args.preserve_manual)
        for manifest, result in results.items():
            print(f"Updated {manifest}: {result['changes']} changes (v{result['version']})")

if __name__ == '__main__':
    main()