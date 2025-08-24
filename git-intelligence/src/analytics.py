#!/usr/bin/env python3
"""
Smart Commit Genie Analytics & Statistics System
Collects usage data, performance metrics, and success rates
"""

import os
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import subprocess


class SmartGenieAnalytics:
    """Collects and analyzes Smart Commit Genie usage statistics"""
    
    def __init__(self):
        self.db_path = Path.home() / ".claude" / "smart-genie-analytics.db"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for analytics"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    feature TEXT NOT NULL,
                    repo_path TEXT,
                    success BOOLEAN,
                    duration_ms INTEGER,
                    details TEXT,
                    user_id TEXT,
                    session_id TEXT
                );
                
                CREATE TABLE IF NOT EXISTS feature_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    feature TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    avg_duration_ms REAL DEFAULT 0,
                    UNIQUE(date, feature)
                );
                
                CREATE TABLE IF NOT EXISTS automation_impact (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    before_value REAL,
                    after_value REAL,
                    improvement_percent REAL,
                    context TEXT
                );
                
                CREATE TABLE IF NOT EXISTS user_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    frequency INTEGER DEFAULT 1,
                    last_seen TEXT,
                    UNIQUE(user_id, pattern_type)
                );
                
                CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_events_feature ON events(feature);
                CREATE INDEX IF NOT EXISTS idx_feature_usage_date ON feature_usage(date);
            """)
            
    def track_event(self, event_type: str, feature: str, success: bool = True, 
                   duration_ms: Optional[int] = None, details: Dict = None):
        """Track a Smart Commit Genie event"""
        try:
            repo_path = os.getcwd()
            user_id = os.environ.get("USER", "unknown")
            session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO events 
                    (timestamp, event_type, feature, repo_path, success, duration_ms, details, user_id, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    event_type,
                    feature,
                    repo_path,
                    success,
                    duration_ms,
                    json.dumps(details or {}),
                    user_id,
                    session_id
                ))
                
            # Update daily aggregates
            self.update_feature_usage(feature, success, duration_ms or 0)
            
        except Exception as e:
            # Silent failure - don't break the main workflow
            if os.environ.get("CLAUDE_DEBUG") == "true":
                print(f"Analytics tracking error: {e}")
                
    def update_feature_usage(self, feature: str, success: bool, duration_ms: int):
        """Update daily feature usage statistics"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            with sqlite3.connect(self.db_path) as conn:
                # Insert or update daily stats
                conn.execute("""
                    INSERT INTO feature_usage (date, feature, usage_count, success_count, avg_duration_ms)
                    VALUES (?, ?, 1, ?, ?)
                    ON CONFLICT(date, feature) DO UPDATE SET
                        usage_count = usage_count + 1,
                        success_count = success_count + ?,
                        avg_duration_ms = (avg_duration_ms * (usage_count - 1) + ?) / usage_count
                """, (today, feature, 1 if success else 0, duration_ms, 1 if success else 0, duration_ms))
                
        except Exception as e:
            if os.environ.get("CLAUDE_DEBUG") == "true":
                print(f"Feature usage update error: {e}")
                
    def track_automation_impact(self, metric: str, before: float, after: float, context: str = ""):
        """Track automation impact measurements"""
        try:
            improvement = ((before - after) / before * 100) if before > 0 else 0
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO automation_impact (timestamp, metric, before_value, after_value, improvement_percent, context)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (datetime.now().isoformat(), metric, before, after, improvement, context))
                
        except Exception as e:
            if os.environ.get("CLAUDE_DEBUG") == "true":
                print(f"Impact tracking error: {e}")
                
    def track_user_pattern(self, pattern_type: str, pattern_data: Dict):
        """Track user behavior patterns"""
        try:
            user_id = os.environ.get("USER", "unknown")
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO user_patterns (user_id, pattern_type, pattern_data, frequency, last_seen)
                    VALUES (?, ?, ?, 1, ?)
                    ON CONFLICT(user_id, pattern_type) DO UPDATE SET
                        frequency = frequency + 1,
                        pattern_data = ?,
                        last_seen = ?
                """, (
                    user_id, 
                    pattern_type, 
                    json.dumps(pattern_data), 
                    datetime.now().isoformat(),
                    json.dumps(pattern_data),
                    datetime.now().isoformat()
                ))
                
        except Exception as e:
            if os.environ.get("CLAUDE_DEBUG") == "true":
                print(f"Pattern tracking error: {e}")
                
    def get_usage_statistics(self, days: int = 30) -> Dict:
        """Get usage statistics for the last N days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            with sqlite3.connect(self.db_path) as conn:
                # Feature usage
                features = conn.execute("""
                    SELECT feature, 
                           SUM(usage_count) as total_usage,
                           SUM(success_count) as total_success,
                           AVG(avg_duration_ms) as avg_duration,
                           ROUND(SUM(success_count) * 100.0 / SUM(usage_count), 2) as success_rate
                    FROM feature_usage 
                    WHERE date >= ? 
                    GROUP BY feature 
                    ORDER BY total_usage DESC
                """, (cutoff_date,)).fetchall()
                
                # Daily activity
                daily_activity = conn.execute("""
                    SELECT date, SUM(usage_count) as daily_usage
                    FROM feature_usage 
                    WHERE date >= ? 
                    GROUP BY date 
                    ORDER BY date DESC
                """, (cutoff_date,)).fetchall()
                
                # Event types
                events = conn.execute("""
                    SELECT event_type, COUNT(*) as count, 
                           AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
                    FROM events 
                    WHERE timestamp >= ? 
                    GROUP BY event_type 
                    ORDER BY count DESC
                """, (cutoff_date,)).fetchall()
                
                # Impact metrics
                impacts = conn.execute("""
                    SELECT metric, AVG(improvement_percent) as avg_improvement
                    FROM automation_impact 
                    WHERE timestamp >= ? 
                    GROUP BY metric
                """, (cutoff_date,)).fetchall()
                
            return {
                "period_days": days,
                "features": [dict(zip([col[0] for col in conn.description], row)) for row in features],
                "daily_activity": [{"date": row[0], "usage": row[1]} for row in daily_activity],
                "events": [dict(zip([col[0] for col in conn.description], row)) for row in events],
                "impact_metrics": [{"metric": row[0], "avg_improvement": row[1]} for row in impacts]
            }
            
        except Exception as e:
            if os.environ.get("CLAUDE_DEBUG") == "true":
                print(f"Statistics retrieval error: {e}")
            return {"error": str(e)}
            
    def get_automation_effectiveness(self) -> Dict:
        """Calculate automation effectiveness metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Time saved by automation
                time_saved = conn.execute("""
                    SELECT SUM(CASE 
                        WHEN feature = 'auto_branch' THEN 30 
                        WHEN feature = 'auto_pr' THEN 300 
                        WHEN feature = 'auto_review' THEN 180 
                        WHEN feature = 'auto_commit' THEN 60 
                        WHEN feature = 'validation' THEN 120 
                        ELSE 30 
                    END) as estimated_time_saved_seconds
                    FROM feature_usage 
                    WHERE date >= date('now', '-30 days')
                """).fetchone()[0] or 0
                
                # Error prevention
                validation_runs = conn.execute("""
                    SELECT COUNT(*) FROM events 
                    WHERE feature = 'validation' AND success = 1 
                    AND timestamp >= datetime('now', '-30 days')
                """).fetchone()[0] or 0
                
                # Workflow automation
                automated_actions = conn.execute("""
                    SELECT COUNT(*) FROM events 
                    WHERE event_type IN ('auto_branch', 'auto_pr', 'auto_commit', 'auto_review')
                    AND timestamp >= datetime('now', '-30 days')
                """).fetchone()[0] or 0
                
            return {
                "estimated_time_saved_hours": round(time_saved / 3600, 2),
                "validation_runs": validation_runs,
                "automated_actions": automated_actions,
                "automation_rate": round((automated_actions / max(validation_runs, 1)) * 100, 2)
            }
            
        except Exception as e:
            return {"error": str(e)}
            
    def generate_report(self) -> str:
        """Generate a human-readable statistics report"""
        stats = self.get_usage_statistics()
        effectiveness = self.get_automation_effectiveness()
        
        report = [
            "🧞‍♂️ Smart Commit Genie - Usage Report",
            "=" * 50,
            f"📊 Last {stats.get('period_days', 30)} days statistics\n"
        ]
        
        # Feature usage
        if stats.get('features'):
            report.append("🚀 Most Used Features:")
            for feature in stats['features'][:5]:
                report.append(f"  • {feature['feature']}: {feature['total_usage']} uses ({feature['success_rate']}% success)")
        
        # Automation effectiveness
        if effectiveness:
            report.extend([
                f"\n⏰ Time Saved: ~{effectiveness['estimated_time_saved_hours']} hours",
                f"🛡️ Validation Runs: {effectiveness['validation_runs']}",
                f"🤖 Automated Actions: {effectiveness['automated_actions']}",
                f"📈 Automation Rate: {effectiveness['automation_rate']}%"
            ])
        
        # Daily activity
        if stats.get('daily_activity'):
            recent_activity = stats['daily_activity'][:7]
            avg_daily = sum(day['usage'] for day in recent_activity) / len(recent_activity)
            report.append(f"\n📅 Average Daily Usage: {avg_daily:.1f} actions")
        
        # Impact metrics
        if stats.get('impact_metrics'):
            report.append("\n📈 Measured Improvements:")
            for metric in stats['impact_metrics']:
                report.append(f"  • {metric['metric']}: {metric['avg_improvement']:.1f}% improvement")
        
        return "\n".join(report)
        
    def export_data(self, format: str = "json") -> str:
        """Export analytics data"""
        if format == "json":
            stats = self.get_usage_statistics()
            effectiveness = self.get_automation_effectiveness()
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "statistics": stats,
                "effectiveness": effectiveness
            }
            
            export_file = Path.home() / ".claude" / f"smart-genie-export-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return str(export_file)
        
        return ""


# Integration functions for other modules
def track_feature_usage(feature: str, start_time: float = None, success: bool = True, details: Dict = None):
    """Track feature usage from any Smart Commit Genie component"""
    try:
        duration = int((time.time() - start_time) * 1000) if start_time else None
        analytics = SmartGenieAnalytics()
        analytics.track_event("feature_use", feature, success, duration, details)
    except:
        pass  # Silent failure


def track_automation_success(automation_type: str, details: Dict = None):
    """Track successful automation"""
    try:
        analytics = SmartGenieAnalytics()
        analytics.track_event("automation", automation_type, True, details=details)
    except:
        pass


def measure_impact(metric: str, before: float, after: float, context: str = ""):
    """Measure automation impact"""
    try:
        analytics = SmartGenieAnalytics()
        analytics.track_automation_impact(metric, before, after, context)
    except:
        pass


if __name__ == "__main__":
    # Generate and print report
    analytics = SmartGenieAnalytics()
    print(analytics.generate_report())