#!/usr/bin/env python3
"""
Context Router - Part of PRISM

Analyzes task descriptions to predict needed context and routes appropriate manifests to agents.
Uses intelligent intent analysis and multi-layer context strategy for optimal performance.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
import hashlib
from collections import defaultdict

# Add git-intelligence src to path for context DNA
sys.path.append(str(Path.home() / 'claude-automations' / 'git-intelligence' / 'src'))

try:
    from context_dna import ContextDNAProfiler, ContextDNA
except ImportError:
    print("[PRISM] Warning: Context DNA not available, using basic routing")
    ContextDNAProfiler = None
    ContextDNA = None

@dataclass
class ContextRoute:
    """Represents a routing decision for context delivery"""
    agent_type: str
    task_intent: str
    confidence: float
    core_manifests: List[str]
    extended_manifests: List[str]
    optional_manifests: List[str]
    estimated_size_kb: float
    routing_reason: str
    
    @property
    def selected_manifests(self) -> Dict[str, float]:
        """Get all selected manifests with relevance scores"""
        result = {}
        # Core manifests get highest relevance
        for m in self.core_manifests:
            result[m] = 0.9
        # Extended manifests get medium relevance
        for m in self.extended_manifests:
            result[m] = 0.7
        # Optional manifests get lower relevance
        for m in self.optional_manifests:
            result[m] = 0.5
        return result
    
    @property
    def relevance_scores(self) -> Dict[str, float]:
        """Alias for selected_manifests for compatibility"""
        return self.selected_manifests
    
    @property
    def detected_intents(self) -> List[str]:
        """Get detected intents from task"""
        return [self.task_intent]
    
    @property
    def confidence_score(self) -> float:
        """Alias for confidence for compatibility"""
        return self.confidence

@dataclass
class TaskIntent:
    """Represents the analyzed intent of a task"""
    primary_domain: str      # 'frontend', 'backend', 'database', 'testing', etc.
    secondary_domains: List[str]
    action_types: List[str]  # 'create', 'update', 'fix', 'optimize', 'test'
    complexity: str          # 'simple', 'medium', 'complex'
    keywords: List[str]
    confidence: float

class ContextRouter:
    """Intelligent context router for agent-specific manifest delivery"""
    
    def __init__(self, manifest_dir: Optional[Path] = None):
        """Initialize the context router"""
        self.manifest_dir = manifest_dir or (Path.home() / '.claude' / 'manifests')
        
        # Initialize context DNA profiler if available
        self.dna_profiler = None
        if ContextDNAProfiler:
            try:
                self.dna_profiler = ContextDNAProfiler()
            except Exception as e:
                print(f"[PRISM] Context DNA profiler failed to initialize: {e}")
        
        # Domain keywords for intent analysis
        self.domain_keywords = {
            'frontend': [
                'component', 'react', 'vue', 'angular', 'ui', 'interface', 'design',
                'style', 'css', 'html', 'jsx', 'tsx', 'state', 'props', 'hook',
                'render', 'dom', 'browser', 'responsive', 'mobile'
            ],
            'backend': [
                'api', 'server', 'endpoint', 'route', 'controller', 'service',
                'middleware', 'auth', 'authentication', 'authorization', 'jwt',
                'session', 'cookie', 'cors', 'http', 'rest', 'graphql'
            ],
            'database': [
                'database', 'db', 'sql', 'query', 'table', 'model', 'schema',
                'migration', 'orm', 'mongodb', 'postgres', 'mysql', 'redis',
                'crud', 'insert', 'update', 'delete', 'select', 'join'
            ],
            'testing': [
                'test', 'spec', 'unit', 'integration', 'e2e', 'mock', 'stub',
                'coverage', 'jest', 'pytest', 'mocha', 'selenium', 'cypress',
                'assert', 'expect', 'should'
            ],
            'devops': [
                'deploy', 'deployment', 'ci/cd', 'pipeline', 'docker', 'kubernetes',
                'aws', 'azure', 'gcp', 'terraform', 'ansible', 'jenkins',
                'github actions', 'build', 'release'
            ],
            'security': [
                'security', 'vulnerability', 'auth', 'encryption', 'ssl', 'tls',
                'hash', 'token', 'csrf', 'xss', 'injection', 'sanitize',
                'validate', 'firewall', 'permissions'
            ],
            'performance': [
                'optimize', 'performance', 'cache', 'cdn', 'compression', 'minify',
                'bundle', 'lazy', 'async', 'concurrent', 'parallel', 'memory',
                'cpu', 'latency', 'throughput'
            ],
            'documentation': [
                'readme', 'docs', 'documentation', 'guide', 'tutorial', 'example',
                'changelog', 'api docs', 'swagger', 'openapi', 'comments'
            ]
        }
        
        # Action keywords
        self.action_keywords = {
            'create': ['create', 'add', 'build', 'implement', 'develop', 'make', 'generate'],
            'update': ['update', 'modify', 'change', 'edit', 'refactor', 'improve'],
            'fix': ['fix', 'bug', 'debug', 'resolve', 'solve', 'repair', 'correct'],
            'remove': ['remove', 'delete', 'cleanup', 'clean', 'clear'],
            'test': ['test', 'verify', 'validate', 'check', 'ensure'],
            'optimize': ['optimize', 'improve', 'enhance', 'speed up', 'performance'],
            'deploy': ['deploy', 'release', 'publish', 'ship'],
            'analyze': ['analyze', 'review', 'audit', 'inspect', 'examine']
        }
        
        # Manifest priorities by domain
        self.domain_manifest_priorities = {
            'frontend': {
                'core': ['COMPONENT_MANIFEST', 'UI_PATTERNS', 'TYPE_DEFINITIONS'],
                'extended': ['API_SURFACE', 'STATE_MANAGEMENT', 'DESIGN_SYSTEM'],
                'optional': ['TEST_MANIFEST', 'PERFORMANCE_PATTERNS']
            },
            'backend': {
                'core': ['API_SURFACE', 'FUNCTION_REGISTRY', 'DATABASE_SCHEMA'],
                'extended': ['SECURITY_PATTERNS', 'ERROR_HANDLING', 'MIDDLEWARE_PATTERNS'],
                'optional': ['DEPLOYMENT_CONFIG', 'PERFORMANCE_PATTERNS']
            },
            'database': {
                'core': ['DATABASE_SCHEMA', 'MODEL_DEFINITIONS'],
                'extended': ['MIGRATION_PATTERNS', 'QUERY_PATTERNS'],
                'optional': ['PERFORMANCE_PATTERNS', 'BACKUP_STRATEGIES']
            },
            'testing': {
                'core': ['TEST_MANIFEST', 'FUNCTION_REGISTRY'],
                'extended': ['COMPONENT_MANIFEST', 'API_SURFACE'],
                'optional': ['COVERAGE_REPORTS', 'MOCK_PATTERNS']
            },
            'devops': {
                'core': ['DEPLOYMENT_CONFIG', 'INFRASTRUCTURE_PATTERNS'],
                'extended': ['SECURITY_PATTERNS', 'MONITORING_CONFIG'],
                'optional': ['BACKUP_STRATEGIES', 'SCALING_PATTERNS']
            },
            'general': {
                'core': ['PROJECT_CONTEXT', 'CODEBASE_MANIFEST'],
                'extended': ['FUNCTION_REGISTRY', 'API_SURFACE'],
                'optional': ['ALL_AVAILABLE']
            }
        }
    
    def analyze_task_intent(self, task_description: str, agent_type: str = 'general') -> TaskIntent:
        """Analyze task description to understand intent"""
        task_lower = task_description.lower()
        words = re.findall(r'\b\w+\b', task_lower)
        
        # Analyze domains
        domain_scores = defaultdict(float)
        matched_keywords = []
        
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    # Score based on exact match vs partial match
                    if keyword in words:
                        domain_scores[domain] += 2.0  # Exact word match
                    else:
                        domain_scores[domain] += 1.0  # Partial match
                    matched_keywords.append(keyword)
        
        # Determine primary and secondary domains
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        primary_domain = sorted_domains[0][0] if sorted_domains else 'general'
        secondary_domains = [domain for domain, score in sorted_domains[1:3] if score > 0]
        
        # Analyze actions
        detected_actions = []
        for action, keywords in self.action_keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    detected_actions.append(action)
                    break
        
        # Determine complexity
        complexity = self._determine_complexity(task_description, len(detected_actions), len(matched_keywords))
        
        # Calculate confidence based on keyword matches and domain clarity
        confidence = min(1.0, (domain_scores[primary_domain] / 10.0) + (len(detected_actions) * 0.1))
        
        return TaskIntent(
            primary_domain=primary_domain,
            secondary_domains=secondary_domains,
            action_types=detected_actions,
            complexity=complexity,
            keywords=matched_keywords,
            confidence=confidence
        )
    
    def route_context(self, task_description: str, agent_type: str = 'general') -> ContextRoute:
        """Route optimal context for the given task and agent"""
        try:
            print(f"[PRISM] Routing context for {agent_type}: {task_description[:100]}...")
            
            # Analyze task intent
            intent = self.analyze_task_intent(task_description, agent_type)
            print(f"[PRISM] Detected intent: {intent.primary_domain} (confidence: {intent.confidence:.2f})")
            
            # Get context route using multiple strategies
            if self.dna_profiler:
                route = self._route_with_dna_profiler(task_description, agent_type, intent)
            else:
                route = self._route_with_heuristics(task_description, agent_type, intent)
            
            print(f"[PRISM] Context route: {len(route.core_manifests)} core, {len(route.extended_manifests)} extended")
            return route
            
        except Exception as e:
            print(f"[PRISM] Error routing context: {e}")
            # Fallback to minimal context
            return self._create_fallback_route(task_description, agent_type)
    
    def _route_with_dna_profiler(self, task: str, agent_type: str, intent: TaskIntent) -> ContextRoute:
        """Route context using DNA profiler intelligence"""
        try:
            # Get optimal context from DNA profiler
            context_package = self.dna_profiler.get_optimal_context(agent_type, task)
            
            # Extract manifest lists
            manifests_loaded = context_package.get('manifests_loaded', [])
            
            # Split into layers based on priority and intent
            core_manifests = []
            extended_manifests = []
            optional_manifests = []
            
            # Get domain priorities
            domain_priorities = self.domain_manifest_priorities.get(
                intent.primary_domain, 
                self.domain_manifest_priorities['general']
            )
            
            for manifest in manifests_loaded:
                if manifest in domain_priorities.get('core', []):
                    core_manifests.append(manifest)
                elif manifest in domain_priorities.get('extended', []):
                    extended_manifests.append(manifest)
                else:
                    optional_manifests.append(manifest)
            
            return ContextRoute(
                agent_type=agent_type,
                task_intent=intent.primary_domain,
                confidence=intent.confidence,
                core_manifests=core_manifests,
                extended_manifests=extended_manifests,
                optional_manifests=optional_manifests,
                estimated_size_kb=context_package.get('context_size_kb', 0.0),
                routing_reason="DNA profiler-based routing with learned patterns"
            )
            
        except Exception as e:
            print(f"[PRISM] DNA profiler routing failed: {e}")
            return self._route_with_heuristics(task, agent_type, intent)
    
    def _route_with_heuristics(self, task: str, agent_type: str, intent: TaskIntent) -> ContextRoute:
        """Route context using heuristic rules"""
        # Get available manifests
        available_manifests = self._get_available_manifests()
        
        # Get domain priorities
        domain_priorities = self.domain_manifest_priorities.get(
            intent.primary_domain,
            self.domain_manifest_priorities['general']
        )
        
        # Filter manifests by availability
        core_manifests = [m for m in domain_priorities.get('core', []) if m in available_manifests]
        extended_manifests = [m for m in domain_priorities.get('extended', []) if m in available_manifests]
        optional_manifests = [m for m in domain_priorities.get('optional', []) if m in available_manifests]
        
        # Add secondary domain manifests to extended
        for secondary_domain in intent.secondary_domains:
            secondary_priorities = self.domain_manifest_priorities.get(secondary_domain, {})
            secondary_core = [m for m in secondary_priorities.get('core', []) if m in available_manifests]
            extended_manifests.extend([m for m in secondary_core if m not in core_manifests])
        
        # Remove duplicates while preserving order
        extended_manifests = list(dict.fromkeys(extended_manifests))
        optional_manifests = list(dict.fromkeys(optional_manifests))
        
        # Estimate size (rough heuristic)
        estimated_size = len(core_manifests) * 5 + len(extended_manifests) * 3 + len(optional_manifests) * 1
        
        return ContextRoute(
            agent_type=agent_type,
            task_intent=intent.primary_domain,
            confidence=intent.confidence,
            core_manifests=core_manifests,
            extended_manifests=extended_manifests,
            optional_manifests=optional_manifests,
            estimated_size_kb=float(estimated_size),
            routing_reason=f"Heuristic routing based on {intent.primary_domain} domain analysis"
        )
    
    def _create_fallback_route(self, task: str, agent_type: str) -> ContextRoute:
        """Create a minimal fallback route when all else fails"""
        available_manifests = self._get_available_manifests()
        
        # Minimal safe manifests
        core_manifests = []
        if 'PROJECT_CONTEXT' in available_manifests:
            core_manifests.append('PROJECT_CONTEXT')
        if 'CODEBASE_MANIFEST' in available_manifests:
            core_manifests.append('CODEBASE_MANIFEST')
        
        return ContextRoute(
            agent_type=agent_type,
            task_intent='general',
            confidence=0.1,
            core_manifests=core_manifests,
            extended_manifests=[],
            optional_manifests=[],
            estimated_size_kb=5.0,
            routing_reason="Fallback routing due to analysis failure"
        )
    
    def _get_available_manifests(self) -> Set[str]:
        """Get list of available manifests"""
        if not self.manifest_dir.exists():
            return set()
        
        available = set()
        
        # Look for common manifest patterns
        for manifest_file in self.manifest_dir.iterdir():
            if manifest_file.is_file():
                # Convert filename to manifest name
                name = manifest_file.stem.upper()
                if name.endswith('_MANIFEST'):
                    available.add(name)
                else:
                    available.add(name)
        
        return available
    
    def _determine_complexity(self, task: str, num_actions: int, num_keywords: int) -> str:
        """Determine task complexity based on various factors"""
        task_length = len(task.split())
        
        # Simple scoring system
        complexity_score = 0
        complexity_score += min(task_length / 20, 3)  # Length factor
        complexity_score += min(num_actions, 3)       # Action diversity
        complexity_score += min(num_keywords / 5, 3)  # Domain breadth
        
        if complexity_score < 2:
            return 'simple'
        elif complexity_score < 5:
            return 'medium'
        else:
            return 'complex'
    
    def create_context_package(self, route: ContextRoute) -> Dict[str, Any]:
        """Create the actual context package based on routing decision"""
        try:
            print(f"[PRISM] Creating context package for {route.agent_type}...")
            
            context = {}
            loaded_manifests = []
            total_size = 0.0
            
            # Load core manifests (always include)
            for manifest_name in route.core_manifests:
                manifest_data = self._load_manifest(manifest_name)
                if manifest_data:
                    context[manifest_name] = manifest_data
                    loaded_manifests.append(manifest_name)
                    total_size += len(json.dumps(manifest_data)) / 1024
            
            # Load extended manifests (include if under size limit)
            size_limit = 50.0  # KB limit for context package
            
            for manifest_name in route.extended_manifests:
                if total_size < size_limit * 0.8:  # Leave room for optional
                    manifest_data = self._load_manifest(manifest_name)
                    if manifest_data:
                        context[manifest_name] = manifest_data
                        loaded_manifests.append(manifest_name)
                        total_size += len(json.dumps(manifest_data)) / 1024
            
            # Load optional manifests (include if still under limit)
            for manifest_name in route.optional_manifests:
                if total_size < size_limit:
                    manifest_data = self._load_manifest(manifest_name)
                    if manifest_data:
                        context[manifest_name] = manifest_data
                        loaded_manifests.append(manifest_name)
                        total_size += len(json.dumps(manifest_data)) / 1024
            
            package = {
                'agent_type': route.agent_type,
                'task_intent': route.task_intent,
                'routing_confidence': route.confidence,
                'manifests_loaded': loaded_manifests,
                'context_size_kb': total_size,
                'routing_reason': route.routing_reason,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"[PRISM] ✅ Context package created: {len(loaded_manifests)} manifests, {total_size:.2f} KB")
            return package
            
        except Exception as e:
            print(f"[PRISM] ❌ Failed to create context package: {e}")
            return {
                'agent_type': route.agent_type,
                'task_intent': 'unknown',
                'routing_confidence': 0.0,
                'manifests_loaded': [],
                'context_size_kb': 0.0,
                'routing_reason': f"Failed to create package: {e}",
                'context': {},
                'timestamp': datetime.now().isoformat()
            }
    
    def _load_manifest(self, manifest_name: str) -> Optional[Dict]:
        """Load a specific manifest file"""
        try:
            # Try different file extensions and naming patterns
            possible_files = [
                self.manifest_dir / f"{manifest_name}.json",
                self.manifest_dir / f"{manifest_name.lower()}.json",
                self.manifest_dir / f"{manifest_name.replace('_', '-').lower()}.json",
                self.manifest_dir / f"{manifest_name}.yaml",
                self.manifest_dir / f"{manifest_name}.yml"
            ]
            
            for manifest_file in possible_files:
                if manifest_file.exists():
                    if manifest_file.suffix in ['.yaml', '.yml']:
                        import yaml
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            return yaml.safe_load(f)
                    else:
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            return json.load(f)
            
            # Manifest not found
            return None
            
        except Exception as e:
            print(f"[PRISM] Error loading manifest {manifest_name}: {e}")
            return None
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get statistics about routing performance"""
        # This would be enhanced with persistent storage in a full implementation
        return {
            'available_manifests': len(self._get_available_manifests()),
            'domain_keywords': len(sum(self.domain_keywords.values(), [])),
            'routing_strategies': 2 if self.dna_profiler else 1,
            'dna_profiler_available': self.dna_profiler is not None,
            'last_updated': datetime.now().isoformat()
        }

def main():
    """Main entry point for context router testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PRISM Context Router')
    parser.add_argument('--task', required=True, help='Task description to route')
    parser.add_argument('--agent', default='general', help='Agent type')
    parser.add_argument('--manifest-dir', help='Manifest directory path')
    parser.add_argument('--stats', action='store_true', help='Show routing statistics')
    
    args = parser.parse_args()
    
    manifest_dir = Path(args.manifest_dir) if args.manifest_dir else None
    router = ContextRouter(manifest_dir)
    
    if args.stats:
        stats = router.get_routing_stats()
        print(json.dumps(stats, indent=2))
        return
    
    # Route the task
    route = router.route_context(args.task, args.agent)
    
    # Create context package
    package = router.create_context_package(route)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"Context Routing Results")
    print(f"{'='*60}")
    print(f"Agent Type: {package['agent_type']}")
    print(f"Task Intent: {package['task_intent']}")
    print(f"Confidence: {package['routing_confidence']:.2f}")
    print(f"Context Size: {package['context_size_kb']:.2f} KB")
    print(f"Manifests Loaded: {', '.join(package['manifests_loaded'])}")
    print(f"Routing Reason: {package['routing_reason']}")

if __name__ == '__main__':
    main()