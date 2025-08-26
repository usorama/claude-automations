#!/usr/bin/env python3
"""
PRISM Simple Dashboard
Terminal-friendly dashboard that always works
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def show_dashboard():
    """Display simple dashboard"""
    db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
    
    if not db_path.exists():
        print("❌ PRISM database not found. Run /prism-activate first.")
        return
    
    print("\n" + "="*60)
    print(" PRISM Intelligence Dashboard ".center(60, "="))
    print("="*60)
    
    with sqlite3.connect(db_path) as conn:
        # Get statistics
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                AVG(context_size_kb) as avg_context,
                AVG(execution_time_ms) as avg_time
            FROM context_usage
            WHERE timestamp > datetime('now', '-24 hours')
        """).fetchone()
        
        if stats and stats[0] > 0:
            success_rate = (stats[1] / stats[0] * 100) if stats[0] else 0
            print(f"\n📊 24-Hour Statistics:")
            print(f"  Total Collections: {stats[0]}")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Avg Context Size: {stats[2]:.1f} KB" if stats[2] else "  Avg Context Size: N/A")
            print(f"  Avg Execution Time: {stats[3]:.0f} ms" if stats[3] else "  Avg Execution Time: N/A")
        else:
            print("\n📊 No data in last 24 hours")
        
        # Get all-time stats
        all_time = conn.execute("""
            SELECT COUNT(*) as total,
                   MIN(timestamp) as first,
                   MAX(timestamp) as last
            FROM context_usage
        """).fetchone()
        
        if all_time and all_time[0] > 0:
            print(f"\n📈 All-Time Stats:")
            print(f"  Total Collections: {all_time[0]}")
            if all_time[1]:
                print(f"  First Collection: {all_time[1][:19]}")
            if all_time[2]:
                print(f"  Last Collection: {all_time[2][:19]}")
        
        # Recent collections
        recent = conn.execute("""
            SELECT agent_type, task_description, timestamp
            FROM context_usage
            ORDER BY timestamp DESC
            LIMIT 5
        """).fetchall()
        
        if recent:
            print(f"\n🕐 Recent Collections:")
            for agent, task, timestamp in recent:
                time_str = timestamp[11:19] if timestamp else "N/A"
                task_short = (task[:40] + "...") if task and len(task) > 40 else (task or "N/A")
                print(f"  [{time_str}] {agent}: {task_short}")
        
        # Check for alerts
        alerts = conn.execute("""
            SELECT severity, message
            FROM alerts
            WHERE acknowledged = 0
            ORDER BY timestamp DESC
            LIMIT 3
        """).fetchall()
        
        if alerts:
            print(f"\n🚨 Active Alerts:")
            for severity, message in alerts:
                print(f"  [{severity.upper()}] {message[:50]}")
        
        # Agent breakdown
        agents = conn.execute("""
            SELECT agent_type, COUNT(*) as count
            FROM context_usage
            GROUP BY agent_type
            ORDER BY count DESC
        """).fetchall()
        
        if agents:
            print(f"\n🤖 Collections by Type:")
            for agent, count in agents:
                print(f"  {agent}: {count}")
    
    print("\n" + "="*60)
    print("\n💡 Tips:")
    print("  • PRISM collects data automatically in background")
    print("  • Run agents to see more data collected")
    print("  • Check /prism health for system status")
    print("")

if __name__ == "__main__":
    show_dashboard()