#!/usr/bin/env python3
"""
PRISM Health Monitor
Monitors system health and prevents silent failures
"""

import sqlite3
import time
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

class PRISMHealthMonitor:
    """Monitors system health and prevents silent failures"""
    
    def __init__(self):
        self.db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
        self.health_checks = {
            'database': self.check_database,
            'manifests': self.check_manifests,
            'hooks': self.check_hooks,
            'learning': self.check_learning,
            'collection': self.check_collection_rate
        }
        self.alert_threshold = {
            'database_size_mb': 100,
            'failure_rate_percent': 30,
            'stale_data_hours': 24,
            'min_collection_rate': 0.1  # At least 1 collection per 10 minutes
        }
        
    def run_health_checks(self) -> Dict[str, Dict]:
        """Run all health checks"""
        results = {}
        overall_status = 'healthy'
        
        for component, check_func in self.health_checks.items():
            try:
                status, message, metrics = check_func()
                results[component] = {
                    'status': status,
                    'message': message,
                    'metrics': metrics,
                    'checked_at': datetime.now().isoformat()
                }
                
                # Record in database
                self.record_health(component, status, message, metrics)
                
                # Update overall status
                if status == 'failed':
                    overall_status = 'failed'
                elif status == 'degraded' and overall_status != 'failed':
                    overall_status = 'degraded'
                
                # Alert if degraded or failed
                if status in ['degraded', 'failed']:
                    self.create_health_alert(component, status, message)
                    
            except Exception as e:
                results[component] = {
                    'status': 'failed',
                    'message': str(e),
                    'metrics': {},
                    'checked_at': datetime.now().isoformat()
                }
                self.create_health_alert(component, 'failed', str(e))
                overall_status = 'failed'
        
        # Add overall status
        results['overall'] = {
            'status': overall_status,
            'components_checked': len(results) - 1,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save health status to file for monitoring
        self.save_health_status(results)
        
        return results
    
    def check_database(self) -> Tuple[str, str, Dict]:
        """Check database health"""
        if not self.db_path.exists():
            return 'failed', 'Database file not found', {'exists': False}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check size
                size_mb = self.db_path.stat().st_size / (1024 * 1024)
                
                # Check recent activity
                recent = conn.execute("""
                    SELECT COUNT(*) FROM context_usage
                    WHERE timestamp > datetime('now', '-1 hour')
                """).fetchone()[0]
                
                # Check failure rate
                stats = conn.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures
                    FROM context_usage
                    WHERE timestamp > datetime('now', '-1 hour')
                """).fetchone()
                
                failure_rate = 0
                if stats and stats[0] > 0:
                    failure_rate = (stats[1] or 0) / stats[0] * 100
                
                # Check table integrity
                tables = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table'
                """).fetchall()
                
                required_tables = ['context_usage', 'alerts', 'learning_patterns']
                missing_tables = [t for t in required_tables if (t,) not in tables]
                
                # Determine status
                status = 'healthy'
                messages = []
                
                if missing_tables:
                    status = 'failed'
                    messages.append(f"Missing tables: {', '.join(missing_tables)}")
                elif size_mb > self.alert_threshold['database_size_mb']:
                    status = 'degraded'
                    messages.append(f"Database size {size_mb:.1f}MB exceeds threshold")
                elif failure_rate > self.alert_threshold['failure_rate_percent']:
                    status = 'degraded'
                    messages.append(f"High failure rate: {failure_rate:.1f}%")
                
                message = '; '.join(messages) if messages else f"Database healthy ({size_mb:.1f}MB, {recent} recent events)"
                
                return status, message, {
                    'size_mb': round(size_mb, 2),
                    'recent_activity': recent,
                    'failure_rate': round(failure_rate, 1),
                    'table_count': len(tables)
                }
                
        except sqlite3.Error as e:
            return 'failed', f"Database error: {e}", {}
    
    def check_manifests(self) -> Tuple[str, str, Dict]:
        """Check manifest generation health"""
        manifest_dir = Path.home() / '.claude' / 'manifests'
        
        if not manifest_dir.exists():
            # Manifests are optional, not a failure
            return 'warning', 'Manifest directory not found', {'exists': False}
        
        manifests = list(manifest_dir.glob('*.json'))
        
        if not manifests:
            return 'warning', 'No manifests found', {'count': 0}
        
        # Check freshness
        now = time.time()
        fresh_count = 0
        stale_count = 0
        
        for manifest in manifests:
            age_hours = (now - manifest.stat().st_mtime) / 3600
            if age_hours < 4:  # Fresh if updated within 4 hours
                fresh_count += 1
            elif age_hours > 24:  # Stale if older than 24 hours
                stale_count += 1
        
        freshness = (fresh_count / len(manifests) * 100) if manifests else 0
        
        # Determine status
        if freshness > 80:
            status = 'healthy'
            message = f"{len(manifests)} manifests, {freshness:.0f}% fresh"
        elif freshness > 50:
            status = 'degraded'
            message = f"{stale_count} stale manifests out of {len(manifests)}"
        else:
            status = 'degraded'
            message = f"Low manifest freshness: {freshness:.0f}%"
        
        return status, message, {
            'manifest_count': len(manifests),
            'fresh_count': fresh_count,
            'stale_count': stale_count,
            'freshness_percent': round(freshness, 1)
        }
    
    def check_hooks(self) -> Tuple[str, str, Dict]:
        """Check if PRISM hooks are properly registered"""
        settings_path = Path.home() / '.claude' / 'settings.json'
        
        if not settings_path.exists():
            return 'warning', 'Claude settings file not found', {'settings_exists': False}
        
        try:
            with open(settings_path) as f:
                settings = json.load(f)
            
            hooks = settings.get('hooks', {})
            prism_hooks_found = []
            
            # Check for PRISM hooks in various hook types
            for hook_type, hook_list in hooks.items():
                if isinstance(hook_list, list):
                    for hook in hook_list:
                        if 'prism' in hook.lower() or 'intelligence' in hook.lower():
                            prism_hooks_found.append(f"{hook_type}: {Path(hook).name}")
            
            if prism_hooks_found:
                status = 'healthy'
                message = f"Found {len(prism_hooks_found)} PRISM hooks registered"
            else:
                status = 'warning'
                message = 'No PRISM hooks registered in settings'
            
            return status, message, {
                'hooks_registered': len(prism_hooks_found),
                'hook_types': list(hooks.keys()),
                'prism_hooks': prism_hooks_found[:3]  # Show first 3
            }
            
        except (json.JSONDecodeError, KeyError) as e:
            return 'failed', f'Error reading settings: {e}', {}
    
    def check_learning(self) -> Tuple[str, str, Dict]:
        """Check if learning is happening"""
        if not self.db_path.exists():
            return 'warning', 'Database not initialized', {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if learning patterns table exists
                tables = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='learning_patterns'
                """).fetchall()
                
                if not tables:
                    return 'warning', 'Learning patterns table not created', {'table_exists': False}
                
                # Check if patterns are being updated
                recent_patterns = conn.execute("""
                    SELECT COUNT(*) FROM learning_patterns
                    WHERE updated_at > datetime('now', '-24 hours')
                """).fetchone()[0]
                
                # Check total patterns
                total_patterns = conn.execute("""
                    SELECT COUNT(*) FROM learning_patterns
                """).fetchone()[0]
                
                # Get average confidence
                avg_confidence = conn.execute("""
                    SELECT AVG(confidence) FROM learning_patterns
                """).fetchone()[0] or 0
            
            if recent_patterns > 0:
                status = 'healthy'
                message = f'Learning active: {recent_patterns} recent patterns, {total_patterns} total'
            elif total_patterns > 0:
                status = 'degraded'
                message = f'Learning stale: no recent updates, {total_patterns} total patterns'
            else:
                status = 'warning'
                message = 'No learning patterns recorded yet'
            
            return status, message, {
                'recent_patterns': recent_patterns,
                'total_patterns': total_patterns,
                'avg_confidence': round(avg_confidence, 3)
            }
            
        except sqlite3.Error as e:
            return 'failed', f'Database error: {e}', {}
    
    def check_collection_rate(self) -> Tuple[str, str, Dict]:
        """Check if data collection is happening at expected rate"""
        if not self.db_path.exists():
            return 'warning', 'Database not initialized', {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get collection rate for last hour
                collections = conn.execute("""
                    SELECT 
                        COUNT(*) as count,
                        MIN(timestamp) as first,
                        MAX(timestamp) as last
                    FROM context_usage
                    WHERE timestamp > datetime('now', '-1 hour')
                """).fetchone()
                
                if not collections or collections[0] == 0:
                    return 'warning', 'No collections in the last hour', {'rate': 0}
                
                # Calculate rate (collections per minute)
                if collections[1] and collections[2]:
                    first = datetime.fromisoformat(collections[1])
                    last = datetime.fromisoformat(collections[2])
                    duration_minutes = (last - first).total_seconds() / 60
                    
                    if duration_minutes > 0:
                        rate = collections[0] / duration_minutes
                    else:
                        rate = collections[0]  # All in same minute
                else:
                    rate = 0
                
                # Check if rate is healthy
                if rate >= self.alert_threshold['min_collection_rate']:
                    status = 'healthy'
                    message = f"Collection rate: {rate:.2f} per minute"
                else:
                    status = 'degraded'
                    message = f"Low collection rate: {rate:.2f} per minute"
                
                return status, message, {
                    'collections_last_hour': collections[0],
                    'rate_per_minute': round(rate, 2)
                }
                
        except sqlite3.Error as e:
            return 'failed', f'Database error: {e}', {}
    
    def record_health(self, component: str, status: str, message: str, metrics: Dict):
        """Record health status to database"""
        if not self.db_path.exists():
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create table if not exists
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_health (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        component TEXT NOT NULL,
                        status TEXT,
                        message TEXT,
                        metrics TEXT
                    )
                """)
                
                conn.execute("""
                    INSERT INTO system_health (component, status, message, metrics)
                    VALUES (?, ?, ?, ?)
                """, (component, status, message, json.dumps(metrics)))
                
        except sqlite3.Error:
            pass  # Silent fail to avoid disrupting health checks
    
    def create_health_alert(self, component: str, status: str, message: str):
        """Create alert for health issues"""
        severity = 'critical' if status == 'failed' else 'warning'
        
        if self.db_path.exists():
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO alerts (severity, component, message, details)
                        VALUES (?, ?, ?, ?)
                    """, (severity, f'health-{component}', message, json.dumps({'status': status})))
            except:
                pass
        
        # Audio notification for failures (macOS only)
        if status == 'failed' and sys.platform == 'darwin':
            try:
                subprocess.run(
                    ['say', f"PRISM component {component} has failed"], 
                    capture_output=True,
                    timeout=5
                )
            except:
                pass
    
    def save_health_status(self, results: Dict):
        """Save health status to file for external monitoring"""
        status_path = Path.home() / '.claude' / 'prism' / 'health_status.json'
        status_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(status_path, 'w') as f:
                json.dump(results, f, indent=2)
        except:
            pass
    
    def auto_remediate(self, component: str, status: str) -> bool:
        """Attempt automatic remediation for known issues"""
        if status != 'failed':
            return False
        
        remediated = False
        
        if component == 'database' and not self.db_path.exists():
            # Try to recreate database
            try:
                from auto_collector import PRISMCollector
                collector = PRISMCollector()
                collector.init_database()
                remediated = True
                print(f"[PRISM] Auto-remediated: Recreated database", file=sys.stderr)
            except:
                pass
        
        elif component == 'hooks':
            # Try to re-register hooks
            # This would need more complex logic to modify settings.json
            pass
        
        return remediated

def main():
    """Main entry point for health monitoring"""
    monitor = PRISMHealthMonitor()
    
    # Run health checks
    results = monitor.run_health_checks()
    
    # Display results
    print("\n" + "="*60)
    print(" PRISM Health Check Results ".center(60, "="))
    print("="*60)
    
    overall_status = results.get('overall', {}).get('status', 'unknown')
    status_emoji = "✅" if overall_status == 'healthy' else "⚠️" if overall_status == 'degraded' else "❌"
    
    print(f"\n{status_emoji} Overall Status: {overall_status.upper()}")
    print(f"Checked at: {results.get('overall', {}).get('timestamp', 'N/A')}")
    
    # Display component results
    print("\nComponent Status:")
    for component, result in results.items():
        if component != 'overall':
            status = result['status']
            message = result['message']
            
            status_icon = "✅" if status == 'healthy' else "⚠️" if status in ['warning', 'degraded'] else "❌"
            print(f"  {status_icon} {component.capitalize()}: {message}")
            
            # Show key metrics
            if result.get('metrics'):
                for key, value in list(result['metrics'].items())[:2]:
                    print(f"      {key}: {value}")
    
    print("\n" + "="*60)
    
    # Return exit code based on status
    if overall_status == 'healthy':
        return 0
    elif overall_status == 'degraded':
        return 1
    else:
        return 2

if __name__ == "__main__":
    sys.exit(main())