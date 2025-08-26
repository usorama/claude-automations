#!/usr/bin/env python3
"""
PRISM Real-Time Dashboard - Shows actual Claude Code usage metrics
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import sys

def get_metrics():
    """Get current PRISM metrics from real data"""
    db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
    
    if not db_path.exists():
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        metrics = {}
        
        # Get tool usage count
        cursor.execute("SELECT COUNT(*) FROM tool_usage")
        metrics['total_tools'] = cursor.fetchone()[0]
        
        # Get agent usage count
        cursor.execute("SELECT COUNT(*) FROM agent_usage")
        metrics['total_agents'] = cursor.fetchone()[0]
        
        # Get file access count
        cursor.execute("SELECT COUNT(*) FROM file_patterns")
        metrics['total_files'] = cursor.fetchone()[0]
        
        # Get search count
        cursor.execute("SELECT COUNT(*) FROM search_patterns")
        metrics['total_searches'] = cursor.fetchone()[0]
        
        # Get command count
        cursor.execute("SELECT COUNT(*) FROM command_patterns")
        metrics['total_commands'] = cursor.fetchone()[0]
        
        # Get top active agents (last 24 hours)
        cursor.execute("""
            SELECT agent_name, COUNT(*) as count
            FROM agent_usage
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY agent_name
            ORDER BY count DESC
            LIMIT 5
        """)
        metrics['active_agents'] = cursor.fetchall()
        
        # Get hot files (most accessed in last 24 hours)
        cursor.execute("""
            SELECT file_path, COUNT(*) as count, MAX(operation) as last_op
            FROM file_patterns
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY file_path
            ORDER BY count DESC
            LIMIT 5
        """)
        metrics['hot_files'] = cursor.fetchall()
        
        # Get recent searches
        cursor.execute("""
            SELECT query, tool, timestamp
            FROM search_patterns
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        metrics['recent_searches'] = cursor.fetchall()
        
        # Get most used tools
        cursor.execute("""
            SELECT tool_name, COUNT(*) as count
            FROM tool_usage
            GROUP BY tool_name
            ORDER BY count DESC
            LIMIT 10
        """)
        metrics['top_tools'] = cursor.fetchall()
        
        # Get success rate for agents
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as rate
            FROM agent_usage
        """)
        result = cursor.fetchone()
        metrics['agent_success_rate'] = round(result[0], 1) if result[0] else 0
        
        # Get file type distribution
        cursor.execute("""
            SELECT extension, COUNT(*) as count
            FROM file_patterns
            WHERE extension != ''
            GROUP BY extension
            ORDER BY count DESC
            LIMIT 5
        """)
        metrics['file_types'] = cursor.fetchall()
        
        # Get command frequency
        cursor.execute("""
            SELECT command, COUNT(*) as count
            FROM command_patterns
            GROUP BY command
            ORDER BY count DESC
            LIMIT 5
        """)
        metrics['top_commands'] = cursor.fetchall()
        
        conn.close()
        return metrics
        
    except Exception as e:
        return {'error': str(e)}

def display_dashboard():
    """Display comprehensive dashboard"""
    metrics = get_metrics()
    
    if not metrics:
        print("\n❌ PRISM database not found.")
        print("   The hooks may not be installed correctly.")
        print("   Check that ~/.claude/hooks symlink points to ~/claude-automations/core/hooks")
        return
    
    if 'error' in metrics:
        print(f"\n❌ Error reading database: {metrics['error']}")
        return
    
    # Header
    print("\n" + "="*80)
    print(" 🔮 PRISM INTELLIGENCE DASHBOARD ".center(80, "="))
    print(" Real-Time Claude Code Usage Metrics ".center(80, "="))
    print("="*80)
    
    # Overall stats box
    print("\n┌─ 📊 COLLECTION STATISTICS " + "─"*51 + "┐")
    print(f"│ Tools Used:     {metrics['total_tools']:>6} │ Agents Run:      {metrics['total_agents']:>6} │ Success Rate: {metrics['agent_success_rate']:>5.1f}% │")
    print(f"│ Files Accessed: {metrics['total_files']:>6} │ Searches Made:   {metrics['total_searches']:>6} │ Commands Run: {metrics['total_commands']:>6}  │")
    print("└" + "─"*78 + "┘")
    
    # Two column layout
    left_col = []
    right_col = []
    
    # Active agents (left)
    if metrics['active_agents']:
        left_col.append("🤖 ACTIVE AGENTS (24H)")
        left_col.append("─" * 35)
        for agent, count in metrics['active_agents']:
            agent_short = agent[:28] if len(agent) > 28 else agent
            left_col.append(f"  {agent_short:<28} {count:>3}x")
        left_col.append("")
    
    # Hot files (right)
    if metrics['hot_files']:
        right_col.append("🔥 HOT FILES (24H)")
        right_col.append("─" * 35)
        for file_path, count, op in metrics['hot_files']:
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path
            file_short = file_name[:25] if len(file_name) > 25 else file_name
            right_col.append(f"  {file_short:<25} {count:>3}x [{op[0]}]")
        right_col.append("")
    
    # Top tools (left)
    if metrics['top_tools']:
        left_col.append("🔧 MOST USED TOOLS")
        left_col.append("─" * 35)
        for tool, count in metrics['top_tools'][:5]:
            left_col.append(f"  {tool:<28} {count:>3}x")
        left_col.append("")
    
    # File types (right)
    if metrics['file_types']:
        right_col.append("📁 FILE TYPE DISTRIBUTION")
        right_col.append("─" * 35)
        for ext, count in metrics['file_types']:
            bar_len = min(20, count * 2)
            bar = "█" * bar_len
            right_col.append(f"  {ext:>6}: {bar:<20} {count:>3}")
        right_col.append("")
    
    # Top commands (left)
    if metrics['top_commands']:
        left_col.append("⚡ TOP COMMANDS")
        left_col.append("─" * 35)
        for cmd, count in metrics['top_commands']:
            left_col.append(f"  {cmd:<28} {count:>3}x")
    
    # Print two columns
    print()
    max_lines = max(len(left_col), len(right_col))
    for i in range(max_lines):
        left = left_col[i] if i < len(left_col) else ""
        right = right_col[i] if i < len(right_col) else ""
        print(f"{left:<39} │ {right:<39}")
    
    # Recent searches
    if metrics['recent_searches']:
        print("\n🔍 RECENT SEARCHES")
        print("─" * 80)
        for query, tool, timestamp in metrics['recent_searches']:
            query_short = query[:50] + "..." if len(query) > 50 else query
            time_str = timestamp[11:19] if timestamp else "N/A"
            print(f"  [{time_str}] [{tool:>6}] {query_short}")
    
    # Footer
    print("\n" + "="*80)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(80))
    print("PRISM is learning from your Claude Code usage patterns...".center(80))
    print("="*80)
    print()

if __name__ == "__main__":
    display_dashboard()