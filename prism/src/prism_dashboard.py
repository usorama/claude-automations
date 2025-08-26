#!/usr/bin/env python3
"""
PRISM Dashboard - Real-time Observability for Manifest Intelligence

Provides real-time visualization and monitoring of PRISM system performance,
showing context size reduction metrics, agent performance, and system health.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import subprocess
from collections import defaultdict, deque

# Add PRISM modules to path
prism_src = Path(__file__).parent
git_intelligence_src = Path.home() / 'claude-automations' / 'git-intelligence' / 'src'
sys.path.extend([str(prism_src), str(git_intelligence_src)])

try:
    from prism_orchestrator import PRISMOrchestrator
    from context_dna import ContextDNAProfiler
except ImportError as e:
    print(f"[PRISM] Warning: Failed to import PRISM component: {e}")
    PRISMOrchestrator = None
    ContextDNAProfiler = None

class PRISMDashboard:
    """Real-time dashboard for PRISM system observability"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the PRISM dashboard"""
        self.project_root = project_root or Path.cwd()
        self.prism_data_dir = Path.home() / '.claude' / 'prism'
        self.prism_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize orchestrator for system access
        self.orchestrator = None
        if PRISMOrchestrator:
            try:
                self.orchestrator = PRISMOrchestrator(self.project_root)
            except Exception as e:
                print(f"[PRISM] Warning: Could not initialize orchestrator: {e}")
        
        # Data collections for real-time monitoring
        self.context_history = deque(maxlen=100)
        self.routing_history = deque(maxlen=100)
        self.health_history = deque(maxlen=50)
        
    def show_live_dashboard(self):
        """Show live dashboard with auto-refresh"""
        try:
            import os
            
            while True:
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                # Show dashboard
                self._render_dashboard()
                
                # Wait for refresh or exit
                time.sleep(5)  # Refresh every 5 seconds
                
        except KeyboardInterrupt:
            print("\n[PRISM] Dashboard stopped")
    
    def show_static_dashboard(self):
        """Show one-time dashboard snapshot"""
        self._render_dashboard()
    
    def _render_dashboard(self):
        """Render the complete dashboard"""
        print("🔬 PRISM Intelligence Dashboard")
        print("=" * 80)
        print(f"📊 Manifest Intelligence System Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # System Overview
        self._render_system_overview()
        
        # Performance Metrics
        self._render_performance_metrics()
        
        # Agent Performance
        self._render_agent_performance()
        
        # Manifest Status
        self._render_manifest_status()
        
        # System Health
        self._render_system_health()
        
        # Recent Activity
        self._render_recent_activity()
        
        print("=" * 80)
        print("🚀 PRISM is optimizing context delivery for maximum agent performance")
        print("📈 Baseline: 200KB+ → Target: <20KB per agent")
        print("=" * 80)
    
    def _render_system_overview(self):
        """Render system overview section"""
        print("\n📋 SYSTEM OVERVIEW")
        print("-" * 40)
        
        try:
            if self.orchestrator:
                status = self.orchestrator.get_system_status()
                
                # Overall status
                status_emoji = {
                    'healthy': '✅',
                    'degraded': '⚠️',
                    'critical': '❌'
                }
                
                overall_status = status.get('status', 'unknown')
                print(f"System Status: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
                
                # Uptime
                uptime_hours = status.get('uptime_hours', 0)
                if uptime_hours < 1:
                    uptime_str = f"{uptime_hours * 60:.0f} minutes"
                elif uptime_hours < 24:
                    uptime_str = f"{uptime_hours:.1f} hours"
                else:
                    uptime_str = f"{uptime_hours / 24:.1f} days"
                
                print(f"System Uptime: {uptime_str}")
                
                # Component status
                components = status.get('components', {})
                print("Component Status:")
                for component, component_status in components.items():
                    emoji = status_emoji.get(component_status, '❓')
                    name = component.replace('_', ' ').title()
                    print(f"  {emoji} {name}: {component_status}")
                
            else:
                print("❌ System status unavailable (orchestrator not running)")
                
        except Exception as e:
            print(f"❌ Error retrieving system status: {e}")
    
    def _render_performance_metrics(self):
        """Render performance metrics section"""
        print("\n📊 PERFORMANCE METRICS")
        print("-" * 40)
        
        try:
            # Load metrics from disk
            metrics_file = self.prism_data_dir / 'metrics.json'
            
            if metrics_file.exists():
                with open(metrics_file) as f:
                    metrics = json.load(f)
                
                # Context size reduction
                size_reduction = metrics.get('context_size_reduction', 0.0)
                avg_size = metrics.get('average_context_size_kb', 200.0)
                
                # Visual bar for size reduction
                bar_length = 30
                reduction_bar = "█" * int(size_reduction * bar_length / 100)
                remaining_bar = "░" * (bar_length - len(reduction_bar))
                
                print(f"Context Size Reduction: {size_reduction:.1f}%")
                print(f"[{reduction_bar}{remaining_bar}] {avg_size:.1f} KB avg")
                
                # Other metrics
                print(f"Routing Accuracy: {metrics.get('routing_accuracy', 0.0):.1f}%")
                print(f"Manifests Updated: {metrics.get('manifests_updated_count', 0)}")
                print(f"Documentation Syncs: {metrics.get('documentation_syncs_count', 0)}")
                print(f"Learning Iterations: {metrics.get('learning_iterations', 0)}")
                
                # Performance goals
                print("\nPerformance Goals:")
                size_goal = "✅" if size_reduction >= 90 else "🎯"
                accuracy_goal = "✅" if metrics.get('routing_accuracy', 0.0) >= 95 else "🎯"
                print(f"  {size_goal} 90% size reduction (currently {size_reduction:.1f}%)")
                print(f"  {accuracy_goal} 95% routing accuracy (currently {metrics.get('routing_accuracy', 0.0):.1f}%)")
                
            else:
                print("📊 No performance metrics available yet")
                print("💡 Metrics will appear after system processes agent requests")
                
        except Exception as e:
            print(f"❌ Error loading performance metrics: {e}")
    
    def _render_agent_performance(self):
        """Render agent performance breakdown"""
        print("\n🤖 AGENT PERFORMANCE")
        print("-" * 40)
        
        try:
            # Load agent statistics from Context DNA
            if ContextDNAProfiler:
                profiler = ContextDNAProfiler()
                
                # Show performance for each agent type
                for agent_type in ['frontend-developer', 'backend-architect', 'test-writer-fixer', 'general']:
                    stats = profiler.get_profile_stats(agent_type)
                    
                    if stats and stats.get('total_usages', 0) > 0:
                        print(f"\n{agent_type.replace('-', ' ').title()}:")
                        print(f"  Usage Count: {stats['total_usages']}")
                        print(f"  Essential Manifests: {stats['essential_count']}")
                        print(f"  Optional Manifests: {stats['optional_count']}")
                        print(f"  Max Context: {stats['max_context_kb']} KB")
                        
                        # Most used manifests
                        if stats.get('most_used'):
                            print(f"  Top Manifest: {stats['most_used'][0][0]} ({stats['most_used'][0][1]} uses)")
            
            else:
                print("❌ Agent performance data unavailable")
                print("💡 Context DNA profiler not initialized")
                
        except Exception as e:
            print(f"❌ Error loading agent performance: {e}")
    
    def _render_manifest_status(self):
        """Render manifest status section"""
        print("\n📁 MANIFEST STATUS")
        print("-" * 40)
        
        try:
            manifest_dir = self.project_root / '.claude' / 'manifests'
            
            if manifest_dir.exists():
                manifests = list(manifest_dir.glob('*'))
                
                print(f"Total Manifests: {len(manifests)}")
                
                # Show manifest sizes
                total_size_kb = 0
                manifest_info = []
                
                for manifest in manifests:
                    if manifest.is_file():
                        size_kb = manifest.stat().st_size / 1024
                        total_size_kb += size_kb
                        manifest_info.append((manifest.name, size_kb))
                
                # Sort by size
                manifest_info.sort(key=lambda x: x[1], reverse=True)
                
                print(f"Total Size: {total_size_kb:.1f} KB")
                print(f"Average Size: {total_size_kb / len(manifest_info):.1f} KB")
                
                print("\nLargest Manifests:")
                for name, size in manifest_info[:5]:
                    print(f"  📄 {name:<25} {size:>8.1f} KB")
                
                # Freshness check
                now = datetime.now()
                fresh_count = 0
                for manifest in manifests:
                    if manifest.is_file():
                        age = now - datetime.fromtimestamp(manifest.stat().st_mtime)
                        if age < timedelta(hours=4):
                            fresh_count += 1
                
                freshness_percent = (fresh_count / len(manifests)) * 100 if manifests else 0
                freshness_emoji = "✅" if freshness_percent >= 80 else "⚠️" if freshness_percent >= 50 else "❌"
                print(f"\nFreshness: {freshness_emoji} {fresh_count}/{len(manifests)} fresh ({freshness_percent:.0f}%)")
                
            else:
                print("❌ No manifest directory found")
                print(f"💡 Expected location: {manifest_dir}")
                
        except Exception as e:
            print(f"❌ Error checking manifest status: {e}")
    
    def _render_system_health(self):
        """Render system health indicators"""
        print("\n💊 SYSTEM HEALTH")
        print("-" * 40)
        
        try:
            if self.orchestrator:
                health = self.orchestrator.check_system_health()
                
                # Component health
                components = {
                    'Context DNA': health.context_dna_status,
                    'Context Router': health.context_router_status,
                    'Manifest Updater': health.manifest_updater_status,
                    'Doc Syncer': health.doc_syncer_status
                }
                
                healthy_count = sum(1 for status in components.values() if status == 'healthy')
                total_count = len(components)
                
                health_emoji = {
                    'healthy': '✅',
                    'degraded': '⚠️',
                    'critical': '❌',
                    'unavailable': '🚫'
                }
                
                print(f"System Health: {healthy_count}/{total_count} components healthy")
                
                for component, status in components.items():
                    emoji = health_emoji.get(status, '❓')
                    print(f"  {emoji} {component}: {status}")
                
                # Performance indicators
                if health.performance_metrics:
                    print("\nKey Performance Indicators:")
                    metrics = health.performance_metrics
                    
                    # Context size trend
                    avg_size = metrics.get('average_context_size_kb', 0)
                    if avg_size <= 20:
                        size_status = "✅ EXCELLENT"
                    elif avg_size <= 50:
                        size_status = "⚠️ GOOD"
                    else:
                        size_status = "❌ NEEDS IMPROVEMENT"
                    print(f"  📏 Avg Context Size: {avg_size:.1f} KB - {size_status}")
                    
                    # Reduction percentage
                    reduction = metrics.get('context_size_reduction_percent', 0)
                    if reduction >= 90:
                        reduction_status = "✅ EXCELLENT"
                    elif reduction >= 70:
                        reduction_status = "⚠️ GOOD"
                    else:
                        reduction_status = "❌ NEEDS IMPROVEMENT"
                    print(f"  📉 Size Reduction: {reduction:.1f}% - {reduction_status}")
                
            else:
                print("❌ Health check unavailable (orchestrator not running)")
                
        except Exception as e:
            print(f"❌ Error checking system health: {e}")
    
    def _render_recent_activity(self):
        """Render recent activity section"""
        print("\n🔄 RECENT ACTIVITY")
        print("-" * 40)
        
        try:
            # Check log files for recent activity
            log_dir = self.prism_data_dir / 'logs'
            
            if log_dir.exists():
                # Find today's log file
                today = datetime.now().strftime('%Y%m%d')
                log_file = log_dir / f"prism_{today}.log"
                
                if log_file.exists():
                    # Read last few lines
                    try:
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                        
                        recent_lines = lines[-10:] if len(lines) >= 10 else lines
                        
                        print("Last 10 log entries:")
                        for line in recent_lines:
                            # Parse log line and show relevant info
                            if 'INFO' in line:
                                parts = line.strip().split(' - ')
                                if len(parts) >= 4:
                                    timestamp = parts[0].split(',')[0]  # Remove milliseconds
                                    message = parts[-1]
                                    time_only = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
                                    print(f"  🔵 {time_only}: {message}")
                            elif 'ERROR' in line:
                                parts = line.strip().split(' - ')
                                if len(parts) >= 4:
                                    timestamp = parts[0].split(',')[0]
                                    message = parts[-1]
                                    time_only = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
                                    print(f"  🔴 {time_only}: {message}")
                            elif 'WARNING' in line:
                                parts = line.strip().split(' - ')
                                if len(parts) >= 4:
                                    timestamp = parts[0].split(',')[0]
                                    message = parts[-1]
                                    time_only = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
                                    print(f"  🟡 {time_only}: {message}")
                                    
                    except Exception as e:
                        print(f"❌ Error reading log file: {e}")
                else:
                    print("📝 No activity logged today")
            else:
                print("📝 No activity logs found")
                
            # Show manifest update activity
            manifest_dir = self.project_root / '.claude' / 'manifests'
            if manifest_dir.exists():
                # Find recently updated manifests
                now = datetime.now()
                recent_updates = []
                
                for manifest in manifest_dir.glob('*'):
                    if manifest.is_file():
                        mtime = datetime.fromtimestamp(manifest.stat().st_mtime)
                        age = now - mtime
                        if age < timedelta(hours=24):
                            recent_updates.append((manifest.name, age))
                
                if recent_updates:
                    recent_updates.sort(key=lambda x: x[1])  # Sort by age
                    print(f"\nRecently Updated Manifests ({len(recent_updates)}):")
                    for name, age in recent_updates[:5]:
                        if age.total_seconds() < 3600:
                            age_str = f"{age.total_seconds() / 60:.0f}m ago"
                        else:
                            age_str = f"{age.total_seconds() / 3600:.1f}h ago"
                        print(f"  📄 {name} - {age_str}")
                        
        except Exception as e:
            print(f"❌ Error showing recent activity: {e}")
    
    def export_dashboard_data(self, output_file: Optional[Path] = None) -> bool:
        """Export dashboard data to JSON file"""
        try:
            if not output_file:
                output_file = self.prism_data_dir / f"dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'project_root': str(self.project_root),
                'system_status': {},
                'performance_metrics': {},
                'manifest_status': {},
                'health_status': {}
            }
            
            # Gather all dashboard data
            if self.orchestrator:
                dashboard_data['system_status'] = self.orchestrator.get_system_status()
                dashboard_data['health_status'] = self.orchestrator.check_system_health()
            
            # Load performance metrics
            metrics_file = self.prism_data_dir / 'metrics.json'
            if metrics_file.exists():
                with open(metrics_file) as f:
                    dashboard_data['performance_metrics'] = json.load(f)
            
            # Manifest status
            manifest_dir = self.project_root / '.claude' / 'manifests'
            if manifest_dir.exists():
                manifests = []
                for manifest in manifest_dir.glob('*'):
                    if manifest.is_file():
                        manifests.append({
                            'name': manifest.name,
                            'size_kb': manifest.stat().st_size / 1024,
                            'last_modified': datetime.fromtimestamp(manifest.stat().st_mtime).isoformat()
                        })
                dashboard_data['manifest_status'] = {
                    'total_count': len(manifests),
                    'manifests': manifests
                }
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(dashboard_data, f, indent=2, default=str)
            
            print(f"[PRISM] Dashboard data exported to: {output_file}")
            return True
            
        except Exception as e:
            print(f"[PRISM] Error exporting dashboard data: {e}")
            return False

def main():
    """Main entry point for PRISM dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PRISM Dashboard - System Observability')
    parser.add_argument('--live', action='store_true', help='Show live dashboard with auto-refresh')
    parser.add_argument('--static', action='store_true', help='Show static dashboard snapshot')
    parser.add_argument('--export', help='Export dashboard data to JSON file')
    parser.add_argument('--project-root', help='Project root directory')
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    dashboard = PRISMDashboard(project_root)
    
    if args.live:
        print("[PRISM] Starting live dashboard... (Press Ctrl+C to exit)")
        dashboard.show_live_dashboard()
    elif args.export:
        output_file = Path(args.export)
        dashboard.export_dashboard_data(output_file)
    else:
        # Default to static dashboard
        dashboard.show_static_dashboard()

if __name__ == '__main__':
    main()