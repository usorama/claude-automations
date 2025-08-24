#!/usr/bin/env python3
"""
Context DNA Profiler - Part of PRISM (Proactive Real-time Intelligence System for Manifests)

This module creates unique DNA profiles for each agent type, showing exactly what context they need.
It learns from usage patterns and optimizes context delivery for maximum efficiency.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional, Any
import json
from pathlib import Path
import hashlib
from datetime import datetime
import re

@dataclass
class ContextDNA:
    """DNA profile for an agent type - defines their context needs"""
    agent_type: str
    essential_manifests: List[str]  # Always load these
    optional_manifests: List[str]   # Load if task matches patterns
    never_manifests: List[str]       # Never load these (proven unnecessary)
    max_context_kb: int              # Size limit for this agent
    task_patterns: Dict[str, List[str]]  # Task keywords -> manifest mapping
    success_patterns: Dict[str, float]  # Context combinations that worked well
    usage_stats: Dict[str, int]     # How often each manifest is actually used
    last_updated: str                # When profile was last updated

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ContextDNA':
        """Create from dictionary"""
        return cls(**data)


class ContextDNAProfiler:
    """Intelligent context profiler that learns what each agent needs"""
    
    # Default DNA profiles for common agent types
    DEFAULT_PROFILES = {
        'frontend-developer': {
            'essential_manifests': ['COMPONENT_MANIFEST', 'UI_PATTERNS', 'TYPE_DEFINITIONS'],
            'optional_manifests': ['API_SURFACE', 'CODE_PATTERNS', 'ERROR_HANDLING'],
            'never_manifests': ['DATABASE_SCHEMA', 'DEPLOYMENT_CONFIG', 'INFRASTRUCTURE'],
            'max_context_kb': 20,
            'task_patterns': {
                'component': ['COMPONENT_MANIFEST', 'UI_PATTERNS'],
                'api|fetch|endpoint': ['API_SURFACE'],
                'style|css|design': ['UI_PATTERNS', 'DESIGN_SYSTEM'],
                'state|redux|context': ['STATE_MANAGEMENT'],
            }
        },
        'backend-architect': {
            'essential_manifests': ['API_SURFACE', 'DATABASE_SCHEMA', 'DEPENDENCY_GRAPH'],
            'optional_manifests': ['ERROR_HANDLING', 'SECURITY_PATTERNS', 'INFRASTRUCTURE'],
            'never_manifests': ['UI_PATTERNS', 'COMPONENT_MANIFEST', 'DESIGN_SYSTEM'],
            'max_context_kb': 30,
            'task_patterns': {
                'database|query|migration': ['DATABASE_SCHEMA', 'DATABASE_PATTERNS'],
                'api|endpoint|route': ['API_SURFACE', 'API_PATTERNS'],
                'auth|security|permission': ['SECURITY_PATTERNS', 'AUTH_CONFIG'],
                'performance|optimize|scale': ['PERFORMANCE_PATTERNS', 'INFRASTRUCTURE'],
            }
        },
        'test-writer-fixer': {
            'essential_manifests': ['FUNCTION_REGISTRY', 'TEST_PATTERNS', 'ERROR_HANDLING'],
            'optional_manifests': ['API_SURFACE', 'COMPONENT_MANIFEST', 'TYPE_DEFINITIONS'],
            'never_manifests': ['DESIGN_SYSTEM', 'UI_PATTERNS', 'DEPLOYMENT_CONFIG'],
            'max_context_kb': 15,
            'task_patterns': {
                'unit|test': ['TEST_PATTERNS', 'FUNCTION_REGISTRY'],
                'integration|e2e': ['API_SURFACE', 'TEST_PATTERNS'],
                'coverage|missing': ['COVERAGE_REPORT', 'FUNCTION_REGISTRY'],
            }
        },
        'general': {
            'essential_manifests': ['PROJECT_CONTEXT', 'CODEBASE_MANIFEST'],
            'optional_manifests': ['FUNCTION_REGISTRY', 'API_SURFACE', 'TYPE_DEFINITIONS'],
            'never_manifests': [],
            'max_context_kb': 25,
            'task_patterns': {}
        }
    }
    
    def __init__(self, profiles_dir: Optional[Path] = None):
        """Initialize the profiler with a directory for storing profiles"""
        self.profiles_dir = profiles_dir or (Path.home() / '.claude' / 'manifests' / 'dna_profiles')
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.profiles = self.load_profiles()
        self.manifest_cache = {}
        
    def load_profiles(self) -> Dict[str, ContextDNA]:
        """Load existing DNA profiles from disk"""
        profiles = {}
        
        # Load saved profiles
        profiles_file = self.profiles_dir / 'profiles.json'
        if profiles_file.exists():
            try:
                data = json.loads(profiles_file.read_text())
                for agent_type, profile_data in data.items():
                    profiles[agent_type] = ContextDNA.from_dict(profile_data)
            except Exception as e:
                print(f"[PRISM] Error loading profiles: {e}")
        
        # Add defaults for any missing agent types
        for agent_type, default_data in self.DEFAULT_PROFILES.items():
            if agent_type not in profiles:
                profiles[agent_type] = ContextDNA(
                    agent_type=agent_type,
                    essential_manifests=default_data['essential_manifests'],
                    optional_manifests=default_data['optional_manifests'],
                    never_manifests=default_data['never_manifests'],
                    max_context_kb=default_data['max_context_kb'],
                    task_patterns=default_data.get('task_patterns', {}),
                    success_patterns={},
                    usage_stats={},
                    last_updated=datetime.now().isoformat()
                )
        
        return profiles
    
    def save_profiles(self):
        """Save current profiles to disk"""
        profiles_file = self.profiles_dir / 'profiles.json'
        data = {
            agent_type: profile.to_dict()
            for agent_type, profile in self.profiles.items()
        }
        profiles_file.write_text(json.dumps(data, indent=2))
        
    def get_optimal_context(self, agent_type: str, task_description: str) -> Dict[str, Any]:
        """Get exactly what this agent needs for this task"""
        # Get or create profile
        profile = self.profiles.get(agent_type, self.profiles['general'])
        
        # Start with essential manifests
        context = {}
        manifests_to_load = set(profile.essential_manifests)
        
        # Add optional manifests based on task analysis
        task_lower = task_description.lower()
        for pattern, manifest_list in profile.task_patterns.items():
            if re.search(pattern, task_lower):
                manifests_to_load.update(manifest_list)
        
        # Remove any never-load manifests
        manifests_to_load -= set(profile.never_manifests)
        
        # Load the manifests
        for manifest_name in manifests_to_load:
            manifest_data = self.load_manifest(manifest_name)
            if manifest_data:
                context[manifest_name] = manifest_data
        
        # Check size and compress if needed
        context_size = self.get_context_size_kb(context)
        if context_size > profile.max_context_kb:
            context = self.compress_context(context, profile, context_size)
        
        # Track usage for learning
        self.track_usage(agent_type, list(manifests_to_load))
        
        return {
            'agent_type': agent_type,
            'task': task_description[:100],  # First 100 chars
            'manifests_loaded': list(manifests_to_load),
            'context_size_kb': self.get_context_size_kb(context),
            'context': context
        }
    
    def load_manifest(self, manifest_name: str) -> Optional[Dict]:
        """Load a specific manifest from cache or disk"""
        # Check cache first
        if manifest_name in self.manifest_cache:
            return self.manifest_cache[manifest_name]
        
        # Try to load from disk
        manifest_path = Path.home() / '.claude' / 'manifests' / f'{manifest_name}.json'
        if manifest_path.exists():
            try:
                data = json.loads(manifest_path.read_text())
                self.manifest_cache[manifest_name] = data
                return data
            except Exception as e:
                print(f"[PRISM] Error loading manifest {manifest_name}: {e}")
        
        return None
    
    def compress_context(self, context: Dict, profile: ContextDNA, current_size: float) -> Dict:
        """Compress context to fit within size limits"""
        target_size = profile.max_context_kb
        compression_ratio = target_size / current_size
        
        compressed = {}
        for manifest_name, manifest_data in context.items():
            # Prioritize essential manifests
            if manifest_name in profile.essential_manifests:
                compressed[manifest_name] = manifest_data
            elif compression_ratio > 0.5:  # Include optional if we have space
                compressed[manifest_name] = self.smart_compress(manifest_data, compression_ratio)
        
        return compressed
    
    def smart_compress(self, data: Any, ratio: float) -> Any:
        """Intelligently compress data by removing less important parts"""
        if isinstance(data, dict):
            # Keep only the most important keys
            num_keys = int(len(data) * ratio)
            important_keys = list(data.keys())[:num_keys]
            return {k: data[k] for k in important_keys}
        elif isinstance(data, list):
            # Keep only first portion of list
            num_items = max(1, int(len(data) * ratio))
            return data[:num_items]
        else:
            return data
    
    def get_context_size_kb(self, context: Dict) -> float:
        """Calculate the size of context in KB"""
        json_str = json.dumps(context)
        return len(json_str) / 1024
    
    def track_usage(self, agent_type: str, manifests_used: List[str]):
        """Track which manifests are actually used by each agent"""
        if agent_type not in self.profiles:
            return
        
        profile = self.profiles[agent_type]
        for manifest in manifests_used:
            profile.usage_stats[manifest] = profile.usage_stats.get(manifest, 0) + 1
        
        profile.last_updated = datetime.now().isoformat()
        
    def learn_from_success(self, agent_type: str, context_combination: List[str], success_score: float):
        """Learn from successful context combinations"""
        if agent_type not in self.profiles:
            return
        
        profile = self.profiles[agent_type]
        combo_key = ','.join(sorted(context_combination))
        
        # Update success pattern with exponential moving average
        current_score = profile.success_patterns.get(combo_key, 0.5)
        profile.success_patterns[combo_key] = (current_score * 0.7) + (success_score * 0.3)
        
        # If this combination is very successful, consider updating defaults
        if profile.success_patterns[combo_key] > 0.8:
            self.optimize_profile(agent_type)
        
        self.save_profiles()
    
    def optimize_profile(self, agent_type: str):
        """Optimize a profile based on learned patterns"""
        if agent_type not in self.profiles:
            return
        
        profile = self.profiles[agent_type]
        
        # Find manifests that are frequently used but not essential
        usage_threshold = 5
        for manifest, count in profile.usage_stats.items():
            if count > usage_threshold and manifest not in profile.essential_manifests:
                if manifest in profile.optional_manifests:
                    # Promote from optional to essential
                    profile.optional_manifests.remove(manifest)
                    profile.essential_manifests.append(manifest)
                    print(f"[PRISM] Promoted {manifest} to essential for {agent_type}")
        
        # Find manifests that are never used
        for manifest in profile.essential_manifests[:]:  # Copy to avoid modification during iteration
            if profile.usage_stats.get(manifest, 0) == 0:
                # Demote from essential to optional
                profile.essential_manifests.remove(manifest)
                if manifest not in profile.optional_manifests:
                    profile.optional_manifests.append(manifest)
                print(f"[PRISM] Demoted {manifest} to optional for {agent_type}")
        
        profile.last_updated = datetime.now().isoformat()
        self.save_profiles()
    
    def get_profile_stats(self, agent_type: str) -> Dict:
        """Get statistics about a profile's performance"""
        if agent_type not in self.profiles:
            return {}
        
        profile = self.profiles[agent_type]
        
        return {
            'agent_type': agent_type,
            'essential_count': len(profile.essential_manifests),
            'optional_count': len(profile.optional_manifests),
            'never_count': len(profile.never_manifests),
            'max_context_kb': profile.max_context_kb,
            'total_usages': sum(profile.usage_stats.values()),
            'most_used': sorted(profile.usage_stats.items(), key=lambda x: x[1], reverse=True)[:5],
            'best_combinations': sorted(profile.success_patterns.items(), key=lambda x: x[1], reverse=True)[:3],
            'last_updated': profile.last_updated
        }


def main():
    """Test the Context DNA Profiler"""
    profiler = ContextDNAProfiler()
    
    # Test different agent scenarios
    test_cases = [
        ('frontend-developer', 'Create a new React component for user dashboard'),
        ('backend-architect', 'Optimize database queries for the user API'),
        ('test-writer-fixer', 'Write unit tests for the authentication module'),
    ]
    
    for agent_type, task in test_cases:
        print(f"\n{'='*60}")
        print(f"Agent: {agent_type}")
        print(f"Task: {task}")
        print(f"{'='*60}")
        
        context = profiler.get_optimal_context(agent_type, task)
        
        print(f"Manifests loaded: {context['manifests_loaded']}")
        print(f"Context size: {context['context_size_kb']:.2f} KB")
        print(f"Stats: {profiler.get_profile_stats(agent_type)}")
    
    # Save profiles
    profiler.save_profiles()
    print("\n[PRISM] Profiles saved successfully")


if __name__ == "__main__":
    main()