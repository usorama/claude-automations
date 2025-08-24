#!/usr/bin/env python3
"""
PRISM Dashboard
Real-time observable metrics dashboard for intelligence monitoring
"""

import sqlite3
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class PRISMDashboard:
    """Real-time observable metrics dashboard"""
    
    def __init__(self):
        self.db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
    def get_metrics(self) -> Dict:
        """Get current metrics from database"""
        if not self.db_path.exists():
            return self._empty_metrics()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Overall stats
                overall = conn.execute("""
                    SELECT 
                        COUNT(*) as total_tasks,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                        AVG(context_size_kb) as avg_context,
                        AVG(execution_time_ms) as avg_time
                    FROM context_usage
                    WHERE timestamp > datetime('now', '-24 hours')
                """).fetchone()
                
                # Recent failures
                failures = conn.execute("""
                    SELECT timestamp, agent_type, error_message
                    FROM context_usage
                    WHERE success = 0
                    ORDER BY timestamp DESC
                    LIMIT 5
                """).fetchall()
                
                # Unacknowledged alerts
                alerts = conn.execute("""
                    SELECT severity, message, timestamp
                    FROM alerts
                    WHERE acknowledged = 0
                    ORDER BY timestamp DESC
                    LIMIT 5
                """).fetchall()
                
                # Agent performance
                agents = conn.execute("""
                    SELECT 
                        agent_type,
                        COUNT(*) as tasks,
                        AVG(context_size_kb) as avg_context,
                        (SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
                    FROM context_usage
                    WHERE timestamp > datetime('now', '-24 hours')
                    GROUP BY agent_type
                    ORDER BY tasks DESC
                    LIMIT 5
                """).fetchall()
                
                # Task type distribution
                task_types = conn.execute("""
                    SELECT 
                        task_type,
                        COUNT(*) as count,
                        (SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
                    FROM context_usage
                    WHERE timestamp > datetime('now', '-24 hours')
                    AND task_type IS NOT NULL
                    GROUP BY task_type
                    ORDER BY count DESC
                """).fetchall()
                
            return {
                'overall': overall,
                'failures': failures,
                'alerts': alerts,
                'agents': agents,
                'task_types': task_types
            }
        except Exception as e:
            print(f"[PRISM] Error getting metrics: {e}", file=sys.stderr)
            return self._empty_metrics()
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'overall': (0, 0, 0, 0),
            'failures': [],
            'alerts': [],
            'agents': [],
            'task_types': []
        }
    
    def format_time(self, timestamp_str: str) -> str:
        """Format timestamp for display"""
        if not timestamp_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(timestamp_str)
            now = datetime.now()
            if dt.date() == now.date():
                return dt.strftime("%H:%M:%S")
            else:
                return dt.strftime("%m/%d %H:%M")
        except:
            return timestamp_str[:19] if len(timestamp_str) > 19 else timestamp_str
    
    def print_simple_dashboard(self):
        """Print simple text dashboard for non-rich environments"""
        metrics = self.get_metrics()
        
        print("\n" + "="*60)
        print(" PRISM Intelligence Dashboard ".center(60, "="))
        print("="*60)
        
        # Overall stats
        overall = metrics['overall']
        if overall and overall[0]:
            success_rate = (overall[1] / overall[0] * 100) if overall[0] > 0 else 0
            print(f"\n📊 24-Hour Statistics:")
            print(f"  Total Tasks: {overall[0]}")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Avg Context Size: {overall[2]:.1f} KB" if overall[2] else "  Avg Context Size: N/A")
            print(f"  Avg Execution Time: {overall[3]:.0f} ms" if overall[3] else "  Avg Execution Time: N/A")
        else:
            print("\n📊 No data collected yet")
        
        # Recent failures
        if metrics['failures']:
            print(f"\n❌ Recent Failures:")
            for failure in metrics['failures'][:3]:
                time_str = self.format_time(failure[0])
                agent = failure[1] or 'unknown'
                error = (failure[2] or 'Unknown error')[:50]
                print(f"  [{time_str}] {agent}: {error}")
        
        # Active alerts
        if metrics['alerts']:
            print(f"\n🚨 Active Alerts:")
            for alert in metrics['alerts'][:3]:
                severity = alert[0].upper()
                message = alert[1][:50]
                print(f"  [{severity}] {message}")
        
        # Agent performance
        if metrics['agents']:
            print(f"\n🤖 Agent Performance:")
            for agent in metrics['agents'][:3]:
                name = agent[0]
                tasks = agent[1]
                success_rate = agent[3] if agent[3] else 0
                print(f"  {name}: {tasks} tasks, {success_rate:.1f}% success")
        
        # Task distribution
        if metrics['task_types']:
            print(f"\n📋 Task Distribution:")
            for task_type in metrics['task_types'][:3]:
                type_name = task_type[0]
                count = task_type[1]
                success_rate = task_type[2] if task_type[2] else 0
                print(f"  {type_name}: {count} tasks, {success_rate:.1f}% success")
        
        print("\n" + "="*60)
    
    def create_rich_dashboard(self) -> Layout:
        """Create rich dashboard layout"""
        if not RICH_AVAILABLE:
            return None
        
        layout = Layout()
        metrics = self.get_metrics()
        
        # Overall stats panel
        overall = metrics['overall']
        stats_table = Table(title="24-Hour Statistics", show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        if overall and overall[0]:
            success_rate = (overall[1] / overall[0] * 100) if overall[0] > 0 else 0
            stats_table.add_row("Total Tasks", str(overall[0]))
            stats_table.add_row("Success Rate", f"{success_rate:.1f}%")
            stats_table.add_row("Avg Context Size", f"{overall[2]:.1f} KB" if overall[2] else "N/A")
            stats_table.add_row("Avg Execution Time", f"{overall[3]:.0f} ms" if overall[3] else "N/A")
        else:
            stats_table.add_row("Status", "No data collected yet")
        
        # Failures panel
        failures_table = Table(title="Recent Failures", show_header=True)
        failures_table.add_column("Time", style="yellow", width=12)
        failures_table.add_column("Agent", style="cyan", width=15)
        failures_table.add_column("Error", style="red", width=30)
        
        for failure in metrics['failures']:
            failures_table.add_row(
                self.format_time(failure[0]),
                failure[1] or 'unknown',
                (failure[2] or 'Unknown')[:30] if failure[2] else 'Unknown'
            )
        
        # Alerts panel
        alerts_table = Table(title="Active Alerts", show_header=True)
        alerts_table.add_column("Severity", style="red", width=10)
        alerts_table.add_column("Message", style="yellow", width=40)
        
        for alert in metrics['alerts']:
            severity_style = "red" if alert[0] == "critical" else "yellow"
            alerts_table.add_row(
                Text(alert[0].upper(), style=severity_style),
                alert[1][:40]
            )
        
        # Agent performance
        agents_table = Table(title="Agent Performance", show_header=True)
        agents_table.add_column("Agent", style="cyan", width=20)
        agents_table.add_column("Tasks", style="white", width=8)
        agents_table.add_column("Success", style="green", width=10)
        agents_table.add_column("Avg Context", style="blue", width=12)
        
        for agent in metrics['agents']:
            agents_table.add_row(
                agent[0][:20],
                str(agent[1]),
                f"{agent[3]:.1f}%" if agent[3] else "0%",
                f"{agent[2]:.1f} KB" if agent[2] else "N/A"
            )
        
        # Combine into layout
        layout.split_column(
            Layout(Panel(stats_table, title="PRISM Intelligence Dashboard", border_style="blue")),
            Layout(name="middle").split_row(
                Layout(Panel(agents_table)),
                Layout(Panel(failures_table))
            ),
            Layout(Panel(alerts_table))
        )
        
        return layout
    
    def run_live(self):
        """Run live dashboard with auto-refresh"""
        if RICH_AVAILABLE and self.console:
            try:
                with Live(self.create_rich_dashboard(), refresh_per_second=0.5, console=self.console) as live:
                    while True:
                        time.sleep(2)
                        live.update(self.create_rich_dashboard())
            except KeyboardInterrupt:
                print("\n[PRISM] Dashboard stopped")
        else:
            # Fallback to simple refresh
            try:
                while True:
                    # Clear screen (Unix/macOS)
                    print("\033[2J\033[H", end="")
                    self.print_simple_dashboard()
                    time.sleep(5)
            except KeyboardInterrupt:
                print("\n[PRISM] Dashboard stopped")
    
    def show_status(self):
        """Show current status (one-time display)"""
        if RICH_AVAILABLE and self.console:
            self.console.print(self.create_rich_dashboard())
        else:
            self.print_simple_dashboard()
    
    def get_health(self) -> Dict:
        """Get system health status"""
        metrics = self.get_metrics()
        
        health = {
            'status': 'healthy',
            'components': {}
        }
        
        # Check database
        if self.db_path.exists():
            size_mb = self.db_path.stat().st_size / (1024 * 1024)
            health['components']['database'] = {
                'status': 'healthy' if size_mb < 100 else 'warning',
                'size_mb': round(size_mb, 2)
            }
        else:
            health['components']['database'] = {
                'status': 'failed',
                'message': 'Database not found'
            }
            health['status'] = 'degraded'
        
        # Check recent activity
        if metrics['overall'] and metrics['overall'][0]:
            total_tasks = metrics['overall'][0]
            success_rate = (metrics['overall'][1] / total_tasks * 100) if total_tasks > 0 else 0
            
            health['components']['collection'] = {
                'status': 'healthy' if success_rate > 80 else 'warning' if success_rate > 50 else 'degraded',
                'tasks_24h': total_tasks,
                'success_rate': round(success_rate, 1)
            }
        else:
            health['components']['collection'] = {
                'status': 'warning',
                'message': 'No recent activity'
            }
        
        # Check for critical alerts
        if metrics['alerts']:
            critical_count = sum(1 for a in metrics['alerts'] if a[0] == 'critical')
            if critical_count > 0:
                health['status'] = 'degraded'
                health['components']['alerts'] = {
                    'status': 'warning',
                    'critical_alerts': critical_count
                }
        
        return health

def main():
    """Main entry point"""
    dashboard = PRISMDashboard()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'status':
            dashboard.show_status()
        elif command == 'health':
            health = dashboard.get_health()
            print(json.dumps(health, indent=2))
        elif command == 'live':
            dashboard.run_live()
        else:
            print("Usage: dashboard.py [status|health|live]")
    else:
        # Default to status
        dashboard.show_status()

if __name__ == "__main__":
    main()