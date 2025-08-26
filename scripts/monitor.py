#!/usr/bin/env python3
"""
Claude Automations Monitoring Dashboard
Real-time visibility into automation status and health.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import time

# Add hook logger to path
sys.path.insert(0, str(Path.home() / 'claude-automations' / 'core' / 'hooks'))
from hook_logger import get_recent_logs

class AutomationMonitor:
    """Monitor all automation systems."""
    
    def __init__(self):
        self.home = Path.home()
        self.claude_auto = self.home / 'claude-automations'
        
    def check_hook_activity(self, hours: int = 24) -> Dict:
        """Check recent hook activity."""
        logs = get_recent_logs(hours)
        
        if not logs:
            return {
                "status": "⚠️ INACTIVE",
                "message": f"No hook activity in last {hours} hours",
                "details": {}
            }
            
        # Analyze logs
        summary = {}
        errors = []
        last_activity = None
        
        for log in logs:
            hook = log.get("hook", "unknown")
            level = log.get("level", "INFO")
            timestamp = log.get("timestamp")
            
            if hook not in summary:
                summary[hook] = {"runs": 0, "errors": 0, "warnings": 0}
                
            summary[hook]["runs"] += 1
            if level == "ERROR":
                summary[hook]["errors"] += 1
                errors.append({
                    "hook": hook,
                    "time": timestamp,
                    "message": log.get("error_message", "Unknown error")
                })
            elif level == "WARNING":
                summary[hook]["warnings"] += 1
                
            if timestamp and (not last_activity or timestamp > last_activity):
                last_activity = timestamp
                
        status = "✅ ACTIVE" if last_activity else "⚠️ INACTIVE"
        
        return {
            "status": status,
            "last_activity": last_activity,
            "summary": summary,
            "recent_errors": errors[-5:] if errors else []
        }
        
    def check_prism_status(self) -> Dict:
        """Check PRISM MCP server status."""
        try:
            # Check if database exists
            db_path = self.claude_auto / 'prism' / 'database' / 'prism.db'
            db_exists = db_path.exists()
            
            # Try to get stats from MCP (would need actual MCP client)
            # For now, check if server is running
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            prism_running = 'prism_mcp_server' in result.stdout
            
            return {
                "database": "✅ EXISTS" if db_exists else "❌ MISSING",
                "server": "✅ RUNNING" if prism_running else "⚠️ UNKNOWN",
                "db_path": str(db_path) if db_exists else None
            }
        except Exception as e:
            return {
                "status": "❌ ERROR",
                "error": str(e)
            }
            
    def check_git_repos(self, repos: List[Path]) -> Dict:
        """Check git repository status."""
        results = {}
        
        for repo in repos:
            if not repo.exists():
                results[repo.name] = {"status": "❌ NOT FOUND"}
                continue
                
            try:
                # Get uncommitted changes count
                os.chdir(repo)
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True,
                    text=True
                )
                uncommitted = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                
                # Get last commit time
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%cr'],
                    capture_output=True,
                    text=True
                )
                last_commit = result.stdout.strip()
                
                # Get branch
                result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True,
                    text=True
                )
                branch = result.stdout.strip()
                
                status = "✅ CLEAN" if uncommitted == 0 else f"⚠️ {uncommitted} UNCOMMITTED"
                
                results[repo.name] = {
                    "status": status,
                    "branch": branch,
                    "last_commit": last_commit,
                    "uncommitted": uncommitted
                }
            except Exception as e:
                results[repo.name] = {"status": "❌ ERROR", "error": str(e)}
                
        return results
        
    def check_cron_jobs(self) -> Dict:
        """Check if auto-commit cron jobs are configured."""
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True
            )
            
            cron_content = result.stdout if result.returncode == 0 else ""
            
            auto_commit_configured = 'auto_commit.sh' in cron_content
            
            return {
                "status": "✅ CONFIGURED" if auto_commit_configured else "❌ NOT CONFIGURED",
                "auto_commit": auto_commit_configured,
                "cron_lines": [line for line in cron_content.split('\n') if 'claude' in line.lower()]
            }
        except Exception as e:
            return {"status": "❌ ERROR", "error": str(e)}
            
    def check_installation(self) -> Dict:
        """Check installation status."""
        checks = {}
        
        # Check symlinks
        symlinks = {
            "commands": self.home / '.claude' / 'commands',
            "hooks": self.home / '.claude' / 'hooks',
            "agents": self.home / '.claude' / 'agents'
        }
        
        for name, path in symlinks.items():
            if path.exists() and path.is_symlink():
                target = path.resolve()
                if target.exists():
                    count = len(list(target.glob('*')))
                    checks[name] = f"✅ {count} items"
                else:
                    checks[name] = "❌ BROKEN LINK"
            else:
                checks[name] = "❌ MISSING"
                
        return checks
        
    def generate_report(self) -> str:
        """Generate comprehensive monitoring report."""
        report = []
        report.append("=" * 60)
        report.append("🔍 CLAUDE AUTOMATIONS MONITORING DASHBOARD")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Installation Status
        report.append("1️⃣  INSTALLATION STATUS")
        report.append("-" * 40)
        installation = self.check_installation()
        for component, status in installation.items():
            report.append(f"  {component}: {status}")
        report.append("")
        
        # Hook Activity
        report.append("2️⃣  HOOK ACTIVITY (Last 24 Hours)")
        report.append("-" * 40)
        hooks = self.check_hook_activity(24)
        report.append(f"  Status: {hooks.get('status', 'UNKNOWN')}")
        if hooks.get('last_activity'):
            report.append(f"  Last Activity: {hooks['last_activity']}")
        if hooks.get('summary'):
            for hook, stats in hooks['summary'].items():
                report.append(f"  {hook}: {stats['runs']} runs")
                if stats.get('errors'):
                    report.append(f"    ❌ Errors: {stats['errors']}")
        if hooks.get('recent_errors'):
            report.append("  Recent Errors:")
            for error in hooks['recent_errors']:
                report.append(f"    - {error['hook']}: {error['message']}")
        report.append("")
        
        # PRISM Status
        report.append("3️⃣  PRISM SYSTEM")
        report.append("-" * 40)
        prism = self.check_prism_status()
        for key, value in prism.items():
            report.append(f"  {key}: {value}")
        report.append("")
        
        # Repository Status
        report.append("4️⃣  REPOSITORY STATUS")
        report.append("-" * 40)
        repos = [
            self.home / 'claude-automations',
            self.home / 'Projects' / 'virtual-tutor'
        ]
        git_status = self.check_git_repos(repos)
        for repo_name, status in git_status.items():
            report.append(f"  {repo_name}:")
            for key, value in status.items():
                report.append(f"    {key}: {value}")
        report.append("")
        
        # Cron Jobs
        report.append("5️⃣  CRON JOBS")
        report.append("-" * 40)
        cron = self.check_cron_jobs()
        report.append(f"  Status: {cron.get('status', 'UNKNOWN')}")
        if cron.get('cron_lines'):
            report.append("  Configured Jobs:")
            for line in cron['cron_lines']:
                if line.strip():
                    report.append(f"    - {line}")
        report.append("")
        
        # Recommendations
        report.append("📋 RECOMMENDATIONS")
        report.append("-" * 40)
        
        recommendations = []
        
        # Check for issues
        if hooks.get('status') == "⚠️ INACTIVE":
            recommendations.append("⚠️  No hook activity - hooks may not be configured properly")
            recommendations.append("   Run: python3 ~/.claude/hooks/hook_logger.py")
            
        if prism.get('database') == "❌ MISSING":
            recommendations.append("⚠️  PRISM database missing")
            recommendations.append("   Run: cd ~/claude-automations/prism/database && sqlite3 prism.db < schema.sql")
            
        if cron.get('status') == "❌ NOT CONFIGURED":
            recommendations.append("⚠️  Auto-commit cron not configured")
            recommendations.append("   Run: crontab -e")
            recommendations.append("   Add: */30 * * * * ~/claude-automations/scripts/auto_commit.sh ~/Projects/virtual-tutor")
            
        for repo_name, status in git_status.items():
            if status.get('uncommitted', 0) > 10:
                recommendations.append(f"⚠️  {repo_name} has {status['uncommitted']} uncommitted files")
                recommendations.append(f"   Run: cd ~/Projects/{repo_name} && git add -A && git commit -m 'WIP: Checkpoint'")
                
        if not recommendations:
            recommendations.append("✅ All systems operational!")
            
        for rec in recommendations:
            report.append(f"  {rec}")
            
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
        
    def run_continuous(self, interval: int = 60):
        """Run continuous monitoring."""
        print("Starting continuous monitoring (Ctrl+C to stop)")
        print(f"Refreshing every {interval} seconds...")
        print()
        
        while True:
            try:
                # Clear screen (works on Unix/Mac)
                os.system('clear')
                
                # Generate and print report
                report = self.generate_report()
                print(report)
                
                # Wait
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\nMonitoring stopped.")
                break


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Claude Automations")
    parser.add_argument('--continuous', '-c', action='store_true',
                      help='Run continuous monitoring')
    parser.add_argument('--interval', '-i', type=int, default=60,
                      help='Refresh interval in seconds (default: 60)')
    
    args = parser.parse_args()
    
    monitor = AutomationMonitor()
    
    if args.continuous:
        monitor.run_continuous(args.interval)
    else:
        print(monitor.generate_report())


if __name__ == "__main__":
    main()