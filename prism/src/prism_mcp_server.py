#!/usr/bin/env python3
"""
PRISM MCP Server - Model Context Protocol Server for PRISM
 
This server provides MCP tools for Claude Code agents to access optimized context
through LLM-driven engineering rather than loading all manifests.

Architecture:
- Supplier: Claude Code hooks collecting data
- Input: Manifests in SQLite database  
- Process: LLM-driven context engineering
- Output: Optimally engineered context
- Customer: Claude Code Agents
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

# MCP imports - using FastMCP for simpler implementation
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    # Fallback for testing without MCP
    MCP_AVAILABLE = False
    class FastMCP:
        def __init__(self, name):
            self.name = name
        def tool(self):
            def decorator(func):
                return func
            return decorator

# Add PRISM modules to path
prism_src = Path(__file__).parent
git_intelligence_src = Path.home() / 'claude-automations' / 'git-intelligence' / 'src'
sys.path.extend([str(prism_src), str(git_intelligence_src)])

# Import PRISM components
try:
    from context_dna import ContextDNAProfiler
    from context_router import ContextRouter
except ImportError as e:
    logging.warning(f"Some PRISM components not available: {e}")
    ContextDNAProfiler = None
    ContextRouter = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[PRISM MCP] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = Path.home() / '.claude' / 'prism' / 'intelligence.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

class PRISMMCPServer:
    """PRISM MCP Server implementation"""
    
    def __init__(self):
        self.mcp = FastMCP("prism")
        self.db_path = DB_PATH
        self.init_database()
        self.context_dna = ContextDNAProfiler() if ContextDNAProfiler else None
        self.context_router = ContextRouter() if ContextRouter else None
        
        # Register MCP tools
        self.register_tools()
    
    def init_database(self):
        """Initialize SQLite database with PRISM schema"""
        with sqlite3.connect(self.db_path) as conn:
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
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_manifests_name ON manifests(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_agent ON usage_patterns(agent_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_session ON context_history(session_id)')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def register_tools(self):
        """Register MCP tools for PRISM functionality"""
        
        @self.mcp.tool()
        def get_optimal_context(
            agent_type: str,
            task_description: str,
            project_path: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get optimized context for an agent's task using LLM-driven selection.
            Quality over quantity - no arbitrary size constraints.
            """
            try:
                logger.info(f"Getting optimal context for {agent_type}: {task_description[:100]}...")
                
                # Load manifests from project or database
                manifests = self.load_available_manifests(project_path)
                
                # Use Context Router if available
                if self.context_router:
                    route = self.context_router.route_context(task_description, agent_type)
                    selected_manifests = route.selected_manifests
                    relevance_scores = route.relevance_scores
                else:
                    # Fallback to profile-based selection
                    selected_manifests = self.select_manifests_by_profile(
                        agent_type, task_description, manifests
                    )
                    relevance_scores = {}
                
                # Build optimized context
                context = self.build_optimized_context(selected_manifests, manifests)
                
                # Track usage for learning
                self.track_usage(
                    agent_type, task_description, 
                    list(selected_manifests.keys()), 
                    context['size_kb']
                )
                
                return {
                    "success": True,
                    "context": context['content'],
                    "manifests_included": list(selected_manifests.keys()),
                    "size_kb": context['size_kb'],
                    "relevance_scores": relevance_scores,
                    "optimization_method": "router" if self.context_router else "profile"
                }
                
            except Exception as e:
                logger.error(f"Error getting optimal context: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "fallback": "Use standard manifest loading"
                }
        
        @self.mcp.tool()
        def analyze_task(
            task: str,
            agent: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Analyze a task to determine context requirements.
            Uses LLM for intent analysis when available.
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
                if self.context_router:
                    route = self.context_router.route_context(task, agent or "general")
                    analysis["detected_intents"] = route.detected_intents
                    analysis["suggested_manifests"] = list(route.selected_manifests.keys())
                    analysis["confidence_score"] = route.confidence_score
                
                # Add agent-specific insights
                if agent and self.context_dna:
                    profile = self.context_dna.get_profile(agent)
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
        
        @self.mcp.tool()
        def update_learning(
            agent: str,
            context_used: List[str],
            success: bool,
            feedback: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Update learning data based on agent feedback.
            Improves future context selection through usage patterns.
            """
            try:
                logger.info(f"Updating learning for {agent}: success={success}")
                
                # Record in database
                with sqlite3.connect(self.db_path) as conn:
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
                if self.context_dna:
                    self.context_dna.update_profile(agent, {
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
        
        @self.mcp.tool()
        def refresh_manifests(
            project_path: str
        ) -> Dict[str, Any]:
            """
            Refresh manifests from a project directory.
            Updates the SQLite database with latest manifest content.
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
                with sqlite3.connect(self.db_path) as conn:
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
        
        @self.mcp.tool()
        def get_prism_stats(self) -> Dict[str, Any]:
            """
            Get PRISM system statistics and health metrics.
            """
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get statistics
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
                    stats['avg_relevance_7d'] = cursor.fetchone()[0] or 0
                    
                    cursor.execute('''
                        SELECT AVG(context_size_kb) FROM usage_patterns
                        WHERE timestamp > datetime('now', '-7 days')
                    ''')
                    stats['avg_context_size_7d'] = cursor.fetchone()[0] or 0
                
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
    
    def load_available_manifests(self, project_path: Optional[str]) -> Dict[str, str]:
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name, content FROM manifests')
                for name, content in cursor.fetchall():
                    if content:
                        manifests[name] = content
        
        return manifests
    
    def select_manifests_by_profile(
        self, agent_type: str, task: str, available: Dict[str, str]
    ) -> Dict[str, float]:
        """Select manifests based on agent profile"""
        selected = {}
        
        # Get agent profile from database
        with sqlite3.connect(self.db_path) as conn:
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
                        selected[manifest] = 0.9  # High relevance for essential
        
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
        self, selected: Dict[str, float], manifests: Dict[str, str]
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
    
    def track_usage(
        self, agent_type: str, task: str, manifests: List[str], size_kb: float
    ):
        """Track usage for learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO usage_patterns 
                    (agent_type, task_description, manifests_used, context_size_kb)
                    VALUES (?, ?, ?, ?)
                ''', (agent_type, task[:500], json.dumps(manifests), size_kb))
                conn.commit()
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
    
    def run(self):
        """Run the MCP server"""
        # For stdio transport, we need to be quiet on stderr
        # Only output MCP protocol on stdout
        import sys
        import io
        
        # Redirect stderr to suppress logging when running as MCP server
        if not os.environ.get('PRISM_DEBUG'):
            sys.stderr = io.StringIO()
        
        # Run using FastMCP's built-in runner
        self.mcp.run(transport='stdio')

def main():
    """Main entry point"""
    try:
        server = PRISMMCPServer()
        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()