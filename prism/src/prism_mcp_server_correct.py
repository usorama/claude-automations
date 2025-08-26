#!/usr/bin/env python3
"""
PRISM MCP Server - Correct Implementation Following MCP Standards

This server provides MCP tools for Claude Code agents to access optimized context
through LLM-driven engineering rather than loading all manifests.
"""

import os
import sys
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

# Add PRISM modules to path
prism_src = Path(__file__).parent
git_intelligence_src = Path.home() / 'claude-automations' / 'git-intelligence' / 'src'
sys.path.extend([str(prism_src), str(git_intelligence_src)])

# Import PRISM components
try:
    from context_dna import ContextDNAProfiler
    from context_router import ContextRouter
    HAS_PRISM_COMPONENTS = True
except ImportError as e:
    HAS_PRISM_COMPONENTS = False
    ContextDNAProfiler = None
    ContextRouter = None

# MCP imports
from mcp.server.fastmcp import FastMCP

# Suppress logging for MCP operation unless debugging
if not os.environ.get('PRISM_DEBUG'):
    logging.basicConfig(level=logging.CRITICAL)
else:
    logging.basicConfig(
        level=logging.INFO,
        format='[PRISM] %(message)s',
        stream=sys.stderr
    )

logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = Path.home() / '.claude' / 'prism' / 'intelligence.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Initialize FastMCP server
mcp = FastMCP("prism")

def init_database():
    """Initialize SQLite database with PRISM schema"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Manifests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manifests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                content TEXT,
                project_path TEXT,
                file_hash TEXT,
                size_kb REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Usage patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_type TEXT,
                task_description TEXT,
                manifests_used TEXT,
                relevance_score REAL,
                success BOOLEAN,
                context_size_kb REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Agent profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_profiles (
                agent_type TEXT PRIMARY KEY,
                essential_manifests TEXT,
                optional_manifests TEXT,
                learning_data TEXT,
                avg_relevance_score REAL,
                total_uses INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Context history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                agent_type TEXT,
                task TEXT,
                context_provided TEXT,
                size_kb REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_manifests_name ON manifests(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_agent ON usage_patterns(agent_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_session ON context_history(session_id)')
        
        conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")

# Initialize database on module load
init_database()

# Initialize PRISM components if available
context_dna = ContextDNAProfiler() if HAS_PRISM_COMPONENTS and ContextDNAProfiler else None
context_router = ContextRouter() if HAS_PRISM_COMPONENTS and ContextRouter else None

@mcp.tool()
def get_optimal_context(
    agent_type: str,
    task_description: str,
    project_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get optimized context for an agent's task using LLM-driven selection.
    Quality over quantity - no arbitrary size constraints.
    
    Args:
        agent_type: Type of agent (e.g., 'frontend-developer', 'backend-architect')
        task_description: Description of the task to be performed
        project_path: Optional path to project directory
    
    Returns:
        Dictionary containing optimized context and metadata
    """
    try:
        logger.info(f"Getting optimal context for {agent_type}: {task_description[:100]}...")
        
        # Load available manifests
        manifests = load_available_manifests(project_path)
        
        # Use Context Router if available
        if context_router:
            route = context_router.route_context(task_description, agent_type)
            selected_manifests = route.selected_manifests
            relevance_scores = route.relevance_scores
        else:
            # Fallback to profile-based selection
            selected_manifests = select_manifests_by_profile(
                agent_type, task_description, manifests
            )
            relevance_scores = {}
        
        # Build optimized context
        context = build_optimized_context(selected_manifests, manifests)
        
        # Track usage for learning
        track_usage(agent_type, task_description, list(selected_manifests.keys()), context['size_kb'])
        
        return {
            "success": True,
            "context": context['content'],
            "manifests_included": list(selected_manifests.keys()),
            "size_kb": context['size_kb'],
            "relevance_scores": relevance_scores,
            "optimization_method": "router" if context_router else "profile"
        }
        
    except Exception as e:
        logger.error(f"Error getting optimal context: {e}")
        return {
            "success": False,
            "error": str(e),
            "fallback": "Use standard manifest loading"
        }

@mcp.tool()
def analyze_task(
    task: str,
    agent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze a task to determine context requirements.
    Uses LLM for intent analysis when available.
    
    Args:
        task: Task description to analyze
        agent: Optional agent type
    
    Returns:
        Analysis results including intents and suggested manifests
    """
    try:
        logger.info(f"Analyzing task: {task[:100]}...")
        
        analysis = {
            "task_summary": task[:200],
            "detected_intents": [],
            "suggested_manifests": [],
            "estimated_context_size": 0
        }
        
        # Use Context Router for analysis if available
        if context_router:
            route = context_router.route_context(task, agent or "general")
            analysis["detected_intents"] = route.detected_intents
            analysis["suggested_manifests"] = list(route.selected_manifests.keys())
            analysis["confidence_score"] = route.confidence_score
        
        # Add agent-specific insights
        if agent and context_dna:
            profile = context_dna.get_profile(agent)
            if profile:
                analysis["agent_profile"] = {
                    "type": agent,
                    "essential_manifests": profile.get('essential_manifests', []),
                    "typical_context_size": profile.get('max_context_kb', 50)
                }
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing task: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def update_learning(
    agent: str,
    context_used: List[str],
    success: bool,
    feedback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update learning data based on agent feedback.
    Improves future context selection through usage patterns.
    
    Args:
        agent: Agent type
        context_used: List of manifests that were used
        success: Whether the task was successful
        feedback: Optional feedback text
    
    Returns:
        Confirmation of learning update
    """
    try:
        logger.info(f"Updating learning for {agent}: success={success}")
        
        # Record in database
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Update usage patterns
            cursor.execute('''
                INSERT INTO usage_patterns 
                (agent_type, manifests_used, success, relevance_score)
                VALUES (?, ?, ?, ?)
            ''', (agent, json.dumps(context_used), success, 0.9 if success else 0.3))
            
            # Update agent profile
            cursor.execute('''
                INSERT OR REPLACE INTO agent_profiles 
                (agent_type, essential_manifests, total_uses, last_updated)
                VALUES (
                    ?,
                    COALESCE((SELECT essential_manifests FROM agent_profiles WHERE agent_type = ?), ?),
                    COALESCE((SELECT total_uses FROM agent_profiles WHERE agent_type = ?), 0) + 1,
                    CURRENT_TIMESTAMP
                )
            ''', (agent, agent, json.dumps(context_used), agent))
            
            conn.commit()
        
        # Update Context DNA if available
        if context_dna:
            context_dna.update_profile(agent, {
                'last_manifests': context_used,
                'success': success,
                'feedback': feedback
            })
        
        return {
            "success": True,
            "message": f"Learning updated for {agent}"
        }
        
    except Exception as e:
        logger.error(f"Error updating learning: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def refresh_manifests(
    project_path: str
) -> Dict[str, Any]:
    """
    Refresh manifests from a project directory.
    Updates the SQLite database with latest manifest content.
    
    Args:
        project_path: Path to project directory
    
    Returns:
        List of updated manifests
    """
    try:
        logger.info(f"Refreshing manifests from {project_path}")
        
        manifest_dir = Path(project_path) / '.claude' / 'manifests'
        if not manifest_dir.exists():
            return {
                "success": False,
                "error": f"No manifests directory at {manifest_dir}"
            }
        
        updated = []
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            for manifest_file in manifest_dir.glob('*'):
                if manifest_file.is_file():
                    content = manifest_file.read_text()
                    file_hash = hashlib.md5(content.encode()).hexdigest()
                    size_kb = len(content) / 1024
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO manifests 
                        (name, content, project_path, file_hash, size_kb, updated_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (manifest_file.name, content, project_path, file_hash, size_kb))
                    
                    updated.append(manifest_file.name)
            
            conn.commit()
        
        return {
            "success": True,
            "manifests_updated": updated,
            "count": len(updated)
        }
        
    except Exception as e:
        logger.error(f"Error refreshing manifests: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def get_prism_stats() -> Dict[str, Any]:
    """
    Get PRISM system statistics and health metrics.
    
    Returns:
        System statistics and health status
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            cursor.execute('SELECT COUNT(*) FROM manifests')
            stats['total_manifests'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM usage_patterns')
            stats['total_uses'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT agent_type) FROM agent_profiles')
            stats['agents_tracked'] = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT AVG(relevance_score) FROM usage_patterns 
                WHERE timestamp > datetime('now', '-7 days')
            ''')
            result = cursor.fetchone()[0]
            stats['avg_relevance_7d'] = result if result else 0
            
            cursor.execute('''
                SELECT AVG(context_size_kb) FROM usage_patterns
                WHERE timestamp > datetime('now', '-7 days')
            ''')
            result = cursor.fetchone()[0]
            stats['avg_context_size_7d'] = result if result else 0
        
        return {
            "success": True,
            "stats": stats,
            "health": "healthy" if stats['total_manifests'] > 0 else "needs_setup"
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Helper functions (not exposed as tools)

def load_available_manifests(project_path: Optional[str]) -> Dict[str, str]:
    """Load manifests from database or project directory"""
    manifests = {}
    
    # Try project directory first
    if project_path:
        manifest_dir = Path(project_path) / '.claude' / 'manifests'
        if manifest_dir.exists():
            for manifest_file in manifest_dir.glob('*'):
                if manifest_file.is_file():
                    manifests[manifest_file.name] = manifest_file.read_text()
    
    # Fall back to database
    if not manifests:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, content FROM manifests')
            for name, content in cursor.fetchall():
                if content:
                    manifests[name] = content
    
    return manifests

def select_manifests_by_profile(
    agent_type: str, task: str, available: Dict[str, str]
) -> Dict[str, float]:
    """Select manifests based on agent profile"""
    selected = {}
    
    # Get agent profile from database
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT essential_manifests FROM agent_profiles WHERE agent_type = ?',
            (agent_type,)
        )
        row = cursor.fetchone()
        
        if row and row[0]:
            essential = json.loads(row[0])
            for manifest in essential:
                if manifest in available:
                    selected[manifest] = 0.9
    
    # If no profile, use defaults based on agent type
    if not selected:
        if 'frontend' in agent_type.lower():
            defaults = ['COMPONENT_MANIFEST.json', 'UI_PATTERNS.md', 'TYPE_DEFINITIONS.ts']
        elif 'backend' in agent_type.lower():
            defaults = ['API_SURFACE.json', 'database-manifest.json', 'FUNCTION_REGISTRY.md']
        else:
            defaults = ['CODEBASE_MANIFEST.yaml', 'FUNCTION_REGISTRY.md']
        
        for manifest in defaults:
            if manifest in available:
                selected[manifest] = 0.7
    
    return selected

def build_optimized_context(
    selected: Dict[str, float], manifests: Dict[str, str]
) -> Dict[str, Any]:
    """Build optimized context from selected manifests"""
    context_parts = []
    total_size = 0
    
    for manifest_name, relevance in sorted(selected.items(), key=lambda x: x[1], reverse=True):
        if manifest_name in manifests:
            content = manifests[manifest_name]
            size = len(content) / 1024
            
            # Add manifest with header
            context_parts.append(f"### {manifest_name} (Relevance: {relevance:.1%})")
            context_parts.append(content)
            context_parts.append("")  # Separator
            
            total_size += size
    
    return {
        'content': '\n'.join(context_parts),
        'size_kb': round(total_size, 2)
    }

def track_usage(agent_type: str, task: str, manifests: List[str], size_kb: float):
    """Track usage for learning"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usage_patterns 
                (agent_type, task_description, manifests_used, context_size_kb)
                VALUES (?, ?, ?, ?)
            ''', (agent_type, task[:500], json.dumps(manifests), size_kb))
            conn.commit()
    except Exception as e:
        logger.error(f"Error tracking usage: {e}")

# Main entry point - FastMCP handles the stdio transport
if __name__ == "__main__":
    # Run the server with stdio transport
    mcp.run(transport='stdio')