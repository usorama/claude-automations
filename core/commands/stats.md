---
command: stats
description: View Smart Commit Genie usage statistics and automation effectiveness
---

Display comprehensive usage statistics and automation effectiveness metrics for Smart Commit Genie.

## Usage
- `/stats` - Show last 30 days statistics
- `/stats 7` - Show last 7 days statistics
- `/stats export` - Export data to JSON file

## How it works
```python
import sys
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from analytics import SmartGenieAnalytics

# Initialize analytics
analytics = SmartGenieAnalytics()

# Check if export requested
if "{{EXPORT}}" == "export":
    export_file = analytics.export_data("json")
    print(f"📊 Data exported to: {export_file}")
else:
    # Get days parameter
    days = 30
    if "{{DAYS}}":
        try:
            days = int("{{DAYS}}")
        except:
            days = 30
    
    # Generate and display report
    print(analytics.generate_report())
    print("\n" + "="*50)
    
    # Get detailed statistics
    stats = analytics.get_usage_statistics(days)
    effectiveness = analytics.get_automation_effectiveness()
    
    # Feature breakdown
    if stats.get('features'):
        print("\n📈 Feature Performance:")
        for feature in stats['features']:
            duration_str = f" (avg: {feature['avg_duration']:.0f}ms)" if feature['avg_duration'] else ""
            print(f"  {feature['feature']}: {feature['total_usage']} uses, {feature['success_rate']}% success{duration_str}")
    
    # Automation effectiveness
    if effectiveness:
        print(f"\n🤖 Automation Effectiveness:")
        print(f"  Time Saved: ~{effectiveness['estimated_time_saved_hours']} hours")
        print(f"  Validation Runs: {effectiveness['validation_runs']}")
        print(f"  Automated Actions: {effectiveness['automated_actions']}")
        print(f"  Success Rate: {effectiveness['automation_rate']}%")
    
    # Recent activity trend
    if stats.get('daily_activity'):
        print(f"\n📅 Recent Activity (last 7 days):")
        for day in stats['daily_activity'][:7]:
            print(f"  {day['date']}: {day['usage']} actions")
    
    # Export option
    print(f"\n💾 Export data: /stats export")
```

## What Gets Tracked

### 🚀 Feature Usage
- **Auto-branching**: Branch creation frequency and success
- **Auto-PR**: PR generation and description quality
- **Auto-review**: Review completion and issue detection
- **Smart merging**: Merge safety and conflict resolution
- **Validation**: Pre-commit checks and auto-fixes
- **Auto-commit**: Background safety commits

### ⏱️ Performance Metrics
- **Execution time**: How fast each feature runs
- **Success rates**: Percentage of successful operations
- **Error patterns**: Common failure modes
- **User satisfaction**: Indirect metrics from usage patterns

### 🎯 Automation Impact
- **Time saved**: Estimated hours saved by automation
- **Errors prevented**: Issues caught by validation
- **Workflow efficiency**: Manual vs automated operations
- **Code quality**: Improvements from automated checks

### 📊 Usage Patterns
- **Daily activity**: Usage trends over time
- **Feature adoption**: Which features are most popular
- **Repository patterns**: Different usage across projects
- **User behavior**: Learning individual preferences

## Example Output

```
🧞‍♂️ Smart Commit Genie - Usage Report
==================================================
📊 Last 30 days statistics

🚀 Most Used Features:
  • auto_commit: 45 uses (98.2% success)
  • validation: 23 uses (87.0% success)  
  • auto_branch: 12 uses (100% success)
  • auto_pr: 8 uses (100% success)
  • auto_review: 6 uses (83.3% success)

⏰ Time Saved: ~3.2 hours
🛡️ Validation Runs: 23
🤖 Automated Actions: 71
📈 Automation Rate: 308%

📅 Average Daily Usage: 2.4 actions

📈 Measured Improvements:
  • commit_quality: 45.2% improvement
  • error_prevention: 78.1% improvement
  • workflow_speed: 34.7% improvement
```

## Data Privacy

All analytics data is stored locally in:
- `~/.claude/smart-genie-analytics.db` (SQLite database)
- No data sent to external services
- User controls all data export and deletion
- Anonymous usage patterns only

## Database Schema

```sql
events: timestamp, event_type, feature, success, duration, details
feature_usage: daily aggregates by feature
automation_impact: before/after measurements
user_patterns: learned behavior patterns
```

## Benefits of Tracking

### 🔍 **Understand Usage**
- Which features provide most value
- Where users encounter problems
- Usage patterns and trends

### 📈 **Measure Impact** 
- Quantify time savings
- Track error prevention
- Demonstrate automation value

### 🎯 **Improve Features**
- Identify slow operations
- Find common failure points
- Optimize based on real usage

### 🏆 **Celebrate Success**
- Show concrete benefits
- Motivate continued usage
- Justify development investment

## Advanced Analytics

### Export Options
```bash
/stats export          # JSON export
/stats 7               # Last week
/stats 90              # Last quarter
```

### Query Examples
The database can be queried directly for custom analysis:
```sql
-- Most successful features
SELECT feature, AVG(success) FROM events GROUP BY feature;

-- Time trends
SELECT date, SUM(usage_count) FROM feature_usage GROUP BY date;

-- Performance analysis
SELECT feature, AVG(duration_ms) FROM events WHERE duration_ms IS NOT NULL;
```

## Tips
- Check stats weekly to see automation impact
- Export data before major system changes
- Use trends to identify optimization opportunities
- Share success metrics with team to promote adoption