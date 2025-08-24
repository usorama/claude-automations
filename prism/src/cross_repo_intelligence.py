#!/usr/bin/env python3
"""
PRISM Cross-Repository Intelligence
Learns patterns across all repositories for smarter recommendations
"""

import sqlite3
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
import hashlib

class CrossRepositoryIntelligence:
    """Learns patterns across all repositories"""
    
    def __init__(self):
        self.db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
        self.cache_dir = Path.home() / '.claude' / 'prism' / 'repo_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.init_tables()
        
    def init_tables(self):
        """Initialize repository patterns table"""
        if not self.db_path.exists():
            return
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS repository_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repository TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_value TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    confidence REAL DEFAULT 0.5
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS repository_metadata (
                    repository TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    last_scanned DATETIME DEFAULT CURRENT_TIMESTAMP,
                    language TEXT,
                    framework TEXT,
                    size_mb REAL,
                    file_count INTEGER,
                    metadata TEXT
                )
            """)
    
    def scan_repository(self, repo_path: Path) -> Dict:
        """Scan a repository for patterns"""
        if not repo_path.exists():
            return {'error': f'Repository path does not exist: {repo_path}'}
        
        repo_name = repo_path.name
        print(f"[PRISM] Scanning repository: {repo_name}")
        
        patterns = {
            'file_structure': self.analyze_structure(repo_path),
            'dependencies': self.analyze_dependencies(repo_path),
            'code_patterns': self.analyze_code_patterns(repo_path),
            'test_patterns': self.analyze_test_patterns(repo_path),
            'git_patterns': self.analyze_git_patterns(repo_path)
        }
        
        # Store patterns
        self.store_patterns(repo_name, patterns)
        
        # Store metadata
        self.store_metadata(repo_name, repo_path, patterns)
        
        return {
            'repository': repo_name,
            'patterns_found': sum(len(v) if isinstance(v, (list, dict)) else 1 for v in patterns.values()),
            'categories': list(patterns.keys())
        }
    
    def analyze_structure(self, repo_path: Path) -> Dict:
        """Analyze repository structure"""
        structure = {
            'directories': [],
            'file_types': {},
            'patterns': [],
            'conventions': []
        }
        
        # Common directories to check
        common_dirs = ['src', 'lib', 'test', 'tests', 'docs', 'config', 'scripts',
                      'components', 'pages', 'api', 'utils', 'hooks', 'services']
        
        for dir_name in common_dirs:
            if (repo_path / dir_name).exists():
                structure['directories'].append(dir_name)
        
        # Analyze file extensions
        for path in repo_path.rglob('*'):
            if path.is_file() and not any(part.startswith('.') for part in path.parts):
                ext = path.suffix
                if ext:
                    structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
        
        # Detect structural patterns
        if 'src' in structure['directories']:
            structure['patterns'].append('src-based')
        if 'lib' in structure['directories']:
            structure['patterns'].append('lib-based')
        if any(d in structure['directories'] for d in ['test', 'tests']):
            structure['patterns'].append('has-tests')
        if 'components' in structure['directories']:
            structure['patterns'].append('component-based')
        
        # Detect conventions
        if (repo_path / 'package.json').exists():
            structure['conventions'].append('node-project')
        if (repo_path / 'requirements.txt').exists() or (repo_path / 'setup.py').exists():
            structure['conventions'].append('python-project')
        if (repo_path / 'Cargo.toml').exists():
            structure['conventions'].append('rust-project')
        if (repo_path / 'go.mod').exists():
            structure['conventions'].append('go-project')
        
        return structure
    
    def analyze_dependencies(self, repo_path: Path) -> Dict:
        """Analyze project dependencies"""
        deps = {
            'package_managers': [],
            'languages': set(),
            'frameworks': [],
            'libraries': {},
            'dev_tools': []
        }
        
        # Check package.json (Node.js)
        package_json = repo_path / 'package.json'
        if package_json.exists():
            deps['package_managers'].append('npm')
            deps['languages'].add('javascript')
            
            try:
                with open(package_json) as f:
                    pkg = json.load(f)
                    
                dependencies = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                
                # Detect frameworks
                framework_indicators = {
                    'react': 'react',
                    'vue': 'vue',
                    'angular': 'angular',
                    'next': 'nextjs',
                    'gatsby': 'gatsby',
                    'express': 'express',
                    'fastify': 'fastify',
                    'svelte': 'svelte'
                }
                
                for indicator, framework in framework_indicators.items():
                    if indicator in dependencies:
                        deps['frameworks'].append(framework)
                
                # Detect dev tools
                dev_tool_indicators = ['jest', 'mocha', 'eslint', 'prettier', 'webpack', 'vite']
                for tool in dev_tool_indicators:
                    if tool in dependencies:
                        deps['dev_tools'].append(tool)
                
                # Store top libraries
                deps['libraries']['npm'] = list(dependencies.keys())[:20]
                
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Check requirements.txt (Python)
        requirements = repo_path / 'requirements.txt'
        if requirements.exists():
            deps['package_managers'].append('pip')
            deps['languages'].add('python')
            
            try:
                with open(requirements) as f:
                    lines = f.readlines()
                    libs = []
                    for line in lines[:20]:  # First 20 dependencies
                        if line.strip() and not line.startswith('#'):
                            lib_name = line.split('==')[0].split('>=')[0].split('~=')[0].strip()
                            libs.append(lib_name)
                    
                    deps['libraries']['pip'] = libs
                    
                    # Detect Python frameworks
                    framework_indicators = {
                        'django': 'django',
                        'flask': 'flask',
                        'fastapi': 'fastapi',
                        'pytest': 'pytest',
                        'numpy': 'data-science',
                        'pandas': 'data-science',
                        'tensorflow': 'machine-learning',
                        'torch': 'machine-learning'
                    }
                    
                    for lib in libs:
                        for indicator, framework in framework_indicators.items():
                            if indicator in lib.lower():
                                if framework not in deps['frameworks']:
                                    deps['frameworks'].append(framework)
                    
            except Exception:
                pass
        
        # Check Cargo.toml (Rust)
        cargo_toml = repo_path / 'Cargo.toml'
        if cargo_toml.exists():
            deps['package_managers'].append('cargo')
            deps['languages'].add('rust')
        
        # Check go.mod (Go)
        go_mod = repo_path / 'go.mod'
        if go_mod.exists():
            deps['package_managers'].append('go')
            deps['languages'].add('go')
        
        # Convert set to list for JSON serialization
        deps['languages'] = list(deps['languages'])
        
        return deps
    
    def analyze_code_patterns(self, repo_path: Path) -> Dict:
        """Analyze code patterns and conventions"""
        patterns = {
            'architecture': [],
            'design_patterns': [],
            'coding_style': [],
            'file_naming': []
        }
        
        # Check for common architecture patterns
        if (repo_path / 'controllers').exists() or (repo_path / 'models').exists():
            patterns['architecture'].append('mvc')
        
        if (repo_path / 'components').exists() and (repo_path / 'hooks').exists():
            patterns['architecture'].append('component-hooks')
        
        if (repo_path / 'domain').exists() or (repo_path / 'application').exists():
            patterns['architecture'].append('ddd')
        
        if (repo_path / 'handlers').exists() or (repo_path / 'middleware').exists():
            patterns['architecture'].append('middleware-based')
        
        # Check file naming conventions
        sample_files = list(repo_path.glob('**/*.py'))[:10] + \
                      list(repo_path.glob('**/*.js'))[:10] + \
                      list(repo_path.glob('**/*.ts'))[:10]
        
        for file_path in sample_files:
            name = file_path.stem
            if '_' in name:
                patterns['file_naming'].append('snake_case')
            elif name[0].isupper():
                patterns['file_naming'].append('PascalCase')
            elif '-' in name:
                patterns['file_naming'].append('kebab-case')
            else:
                patterns['file_naming'].append('camelCase')
        
        # Deduplicate
        patterns['file_naming'] = list(set(patterns['file_naming']))
        
        # Check for common patterns in code structure
        if (repo_path / 'utils').exists() or (repo_path / 'helpers').exists():
            patterns['design_patterns'].append('utility-functions')
        
        if (repo_path / 'factories').exists():
            patterns['design_patterns'].append('factory-pattern')
        
        if (repo_path / 'services').exists():
            patterns['design_patterns'].append('service-layer')
        
        return patterns
    
    def analyze_test_patterns(self, repo_path: Path) -> Dict:
        """Analyze testing patterns"""
        patterns = {
            'test_framework': [],
            'test_location': [],
            'test_types': [],
            'coverage': False
        }
        
        # Check test locations
        if (repo_path / 'tests').exists():
            patterns['test_location'].append('tests-directory')
        if (repo_path / 'test').exists():
            patterns['test_location'].append('test-directory')
        if (repo_path / '__tests__').exists():
            patterns['test_location'].append('__tests__-directory')
        
        # Check for test files alongside source
        if list(repo_path.glob('**/*.test.js')) or list(repo_path.glob('**/*.spec.js')):
            patterns['test_location'].append('colocated-tests')
        
        # Detect test frameworks
        test_files = list(repo_path.glob('**/*test*.py')) + \
                    list(repo_path.glob('**/*test*.js')) + \
                    list(repo_path.glob('**/*spec*.js'))
        
        for test_file in test_files[:5]:  # Sample first 5
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(500)  # Read first 500 chars
                    
                    # JavaScript/TypeScript frameworks
                    if 'jest' in content.lower() or 'expect(' in content:
                        patterns['test_framework'].append('jest')
                    if 'mocha' in content.lower() or 'describe(' in content:
                        patterns['test_framework'].append('mocha')
                    if 'vitest' in content.lower():
                        patterns['test_framework'].append('vitest')
                    
                    # Python frameworks
                    if 'pytest' in content.lower() or 'def test_' in content:
                        patterns['test_framework'].append('pytest')
                    if 'unittest' in content.lower():
                        patterns['test_framework'].append('unittest')
                    
                    # Test types
                    if 'unit' in test_file.name.lower():
                        patterns['test_types'].append('unit')
                    if 'integration' in test_file.name.lower():
                        patterns['test_types'].append('integration')
                    if 'e2e' in test_file.name.lower():
                        patterns['test_types'].append('e2e')
                        
            except Exception:
                pass
        
        # Check for coverage config
        if (repo_path / '.coveragerc').exists() or \
           (repo_path / 'jest.config.js').exists() or \
           (repo_path / 'coverage').exists():
            patterns['coverage'] = True
        
        # Deduplicate
        patterns['test_framework'] = list(set(patterns['test_framework']))
        patterns['test_types'] = list(set(patterns['test_types']))
        
        return patterns
    
    def analyze_git_patterns(self, repo_path: Path) -> Dict:
        """Analyze git patterns"""
        patterns = {
            'branch_strategy': [],
            'commit_style': [],
            'workflow': []
        }
        
        # Check for CI/CD files
        ci_files = {
            '.github/workflows': 'github-actions',
            '.gitlab-ci.yml': 'gitlab-ci',
            '.circleci': 'circleci',
            'Jenkinsfile': 'jenkins',
            '.travis.yml': 'travis'
        }
        
        for ci_path, ci_type in ci_files.items():
            if (repo_path / ci_path).exists():
                patterns['workflow'].append(ci_type)
        
        # Try to detect branch strategy from git
        try:
            result = subprocess.run(
                ['git', 'branch', '-r'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                branches = result.stdout.lower()
                if 'develop' in branches:
                    patterns['branch_strategy'].append('git-flow')
                if 'main' in branches or 'master' in branches:
                    patterns['branch_strategy'].append('main-branch')
                if 'release' in branches:
                    patterns['branch_strategy'].append('release-branches')
                    
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Check commit message style from recent commits
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '-10'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                commits = result.stdout.lower()
                if 'feat:' in commits or 'fix:' in commits:
                    patterns['commit_style'].append('conventional-commits')
                if '[' in commits and ']' in commits:
                    patterns['commit_style'].append('bracketed-tags')
                    
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return patterns
    
    def store_patterns(self, repo_name: str, patterns: Dict):
        """Store patterns in database"""
        with sqlite3.connect(self.db_path) as conn:
            for pattern_type, pattern_data in patterns.items():
                if isinstance(pattern_data, dict):
                    for key, value in pattern_data.items():
                        if isinstance(value, list):
                            for item in value:
                                self._store_single_pattern(conn, repo_name, f"{pattern_type}.{key}", str(item))
                        else:
                            self._store_single_pattern(conn, repo_name, f"{pattern_type}.{key}", str(value))
                elif isinstance(pattern_data, list):
                    for item in pattern_data:
                        self._store_single_pattern(conn, repo_name, pattern_type, str(item))
    
    def _store_single_pattern(self, conn, repo_name: str, pattern_type: str, pattern_value: str):
        """Store a single pattern"""
        # Check if pattern exists
        existing = conn.execute("""
            SELECT id, frequency FROM repository_patterns
            WHERE repository = ? AND pattern_type = ? AND pattern_value = ?
        """, (repo_name, pattern_type, pattern_value)).fetchone()
        
        if existing:
            # Update existing pattern
            conn.execute("""
                UPDATE repository_patterns
                SET frequency = frequency + 1, last_seen = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (existing[0],))
        else:
            # Insert new pattern
            conn.execute("""
                INSERT INTO repository_patterns (repository, pattern_type, pattern_value, frequency)
                VALUES (?, ?, ?, 1)
            """, (repo_name, pattern_type, pattern_value))
    
    def store_metadata(self, repo_name: str, repo_path: Path, patterns: Dict):
        """Store repository metadata"""
        # Calculate repository size
        total_size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file()) / (1024 * 1024)
        file_count = len(list(repo_path.rglob('*')))
        
        # Determine primary language and framework
        deps = patterns.get('dependencies', {})
        languages = deps.get('languages', [])
        frameworks = deps.get('frameworks', [])
        
        primary_language = languages[0] if languages else 'unknown'
        primary_framework = frameworks[0] if frameworks else None
        
        metadata = {
            'patterns_summary': {
                'architecture': patterns.get('code_patterns', {}).get('architecture', []),
                'test_frameworks': patterns.get('test_patterns', {}).get('test_framework', []),
                'ci_cd': patterns.get('git_patterns', {}).get('workflow', [])
            }
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO repository_metadata 
                (repository, path, language, framework, size_mb, file_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (repo_name, str(repo_path), primary_language, primary_framework, 
                  round(total_size, 2), file_count, json.dumps(metadata)))
    
    def get_recommendations(self, current_repo: str) -> List[Dict]:
        """Get recommendations based on cross-repo patterns"""
        recommendations = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Get current repo metadata
            current_meta = conn.execute("""
                SELECT language, framework FROM repository_metadata
                WHERE repository = ?
            """, (current_repo,)).fetchone()
            
            if not current_meta:
                return recommendations
            
            current_lang, current_framework = current_meta
            
            # Find similar repositories
            similar = conn.execute("""
                SELECT DISTINCT r1.repository 
                FROM repository_metadata r1
                WHERE r1.language = ? 
                AND r1.repository != ?
                LIMIT 5
            """, (current_lang, current_repo)).fetchall()
            
            # Get patterns from similar repos that current doesn't have
            for (similar_repo,) in similar:
                patterns = conn.execute("""
                    SELECT pattern_type, pattern_value, confidence
                    FROM repository_patterns
                    WHERE repository = ?
                    AND pattern_value NOT IN (
                        SELECT pattern_value FROM repository_patterns
                        WHERE repository = ?
                    )
                    AND confidence > 0.5
                    ORDER BY confidence DESC
                    LIMIT 3
                """, (similar_repo, current_repo)).fetchall()
                
                for pattern_type, pattern_value, confidence in patterns:
                    recommendations.append({
                        'source': similar_repo,
                        'pattern': pattern_type,
                        'value': pattern_value,
                        'confidence': round(confidence, 2),
                        'recommendation': self._generate_recommendation(pattern_type, pattern_value, similar_repo)
                    })
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _generate_recommendation(self, pattern_type: str, pattern_value: str, source_repo: str) -> str:
        """Generate human-readable recommendation"""
        recommendations_map = {
            'dependencies.frameworks': f"Consider adopting {pattern_value} framework (used successfully in {source_repo})",
            'dependencies.dev_tools': f"Add {pattern_value} to improve development workflow (proven in {source_repo})",
            'test_patterns.test_framework': f"Implement {pattern_value} for testing (effective in {source_repo})",
            'code_patterns.architecture': f"Consider {pattern_value} architecture pattern (working well in {source_repo})",
            'git_patterns.workflow': f"Set up {pattern_value} for CI/CD (automated in {source_repo})"
        }
        
        # Check if we have a specific recommendation
        for key_pattern, recommendation_template in recommendations_map.items():
            if pattern_type.startswith(key_pattern.split('.')[0]):
                return recommendation_template
        
        # Default recommendation
        return f"Consider adopting {pattern_value} from {source_repo}"
    
    def scan_all_projects(self, base_path: Path = None) -> Dict:
        """Scan all projects in a directory"""
        if base_path is None:
            base_path = Path.home() / 'Projects'
        
        if not base_path.exists():
            return {'error': f'Base path does not exist: {base_path}'}
        
        results = {
            'scanned': [],
            'failed': [],
            'total_patterns': 0
        }
        
        # Find all git repositories
        for repo_dir in base_path.iterdir():
            if repo_dir.is_dir() and (repo_dir / '.git').exists():
                try:
                    scan_result = self.scan_repository(repo_dir)
                    results['scanned'].append(scan_result)
                    results['total_patterns'] += scan_result.get('patterns_found', 0)
                except Exception as e:
                    results['failed'].append({
                        'repository': repo_dir.name,
                        'error': str(e)
                    })
        
        return results

def main():
    """Main entry point for cross-repo intelligence"""
    import sys
    
    intelligence = CrossRepositoryIntelligence()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'scan' and len(sys.argv) > 2:
            # Scan specific repository
            repo_path = Path(sys.argv[2])
            result = intelligence.scan_repository(repo_path)
            print(json.dumps(result, indent=2))
            
        elif command == 'scan-all':
            # Scan all projects
            base_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
            results = intelligence.scan_all_projects(base_path)
            print(f"\nScanned {len(results['scanned'])} repositories")
            print(f"Total patterns found: {results['total_patterns']}")
            if results['failed']:
                print(f"Failed to scan: {len(results['failed'])} repositories")
                
        elif command == 'recommend' and len(sys.argv) > 2:
            # Get recommendations for repository
            repo_name = sys.argv[2]
            recommendations = intelligence.get_recommendations(repo_name)
            
            if recommendations:
                print(f"\n🎯 Recommendations for {repo_name}:\n")
                for rec in recommendations:
                    print(f"  • {rec['recommendation']}")
                    print(f"    Confidence: {rec['confidence']}")
            else:
                print(f"No recommendations available for {repo_name}")
        else:
            print("Usage:")
            print("  cross_repo_intelligence.py scan <repo_path>")
            print("  cross_repo_intelligence.py scan-all [base_path]")
            print("  cross_repo_intelligence.py recommend <repo_name>")
    else:
        print("Cross-Repository Intelligence System")
        print("Usage:")
        print("  cross_repo_intelligence.py scan <repo_path>")
        print("  cross_repo_intelligence.py scan-all [base_path]")
        print("  cross_repo_intelligence.py recommend <repo_name>")

if __name__ == "__main__":
    main()