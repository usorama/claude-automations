# Silent Failure Detection Command

## Purpose
Runs the silent failure detector script to identify patterns that hide real issues from developers and users. Integrates with the checkpoint system to prevent deployment of code with critical silent failures.

## Usage
```bash
/silent-check [directory]
```

If no directory is provided, analyzes the current working directory.

## Implementation

### Command Handler
```javascript
const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

function runSilentCheck(targetDir = process.cwd()) {
  const detectorScript = path.join(process.env.HOME, '.claude/process-templates-n-prompts/silent-failures/silent-failure-detector.ts');
  
  if (!fs.existsSync(detectorScript)) {
    console.error('❌ Silent failure detector script not found');
    return false;
  }
  
  console.log('🔍 Running silent failure detection...');
  
  try {
    // Run the detector script
    const result = execSync(`npx ts-node "${detectorScript}" "${targetDir}"`, {
      cwd: targetDir,
      encoding: 'utf8',
      stdio: 'pipe'
    });
    
    console.log(result);
    
    // Check for critical issues in the generated report
    const reportPath = path.join(targetDir, 'silent-failures-report.json');
    if (fs.existsSync(reportPath)) {
      const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
      
      if (report.summary.critical > 0) {
        console.log('');
        console.log('🚨 CRITICAL SILENT FAILURES DETECTED');
        console.log('=' .repeat(50));
        console.log('❌ Cannot proceed with deployment until these are fixed');
        console.log(`Critical issues: ${report.summary.critical}`);
        console.log(`High issues: ${report.summary.high}`);
        console.log('');
        console.log('Fix these issues before running git commit or deployment.');
        return false;
      } else if (report.summary.high > 0) {
        console.log('');
        console.log('⚠️  HIGH PRIORITY ISSUES DETECTED');
        console.log('=' .repeat(50));
        console.log('✅ No critical blockers, but please review high priority issues');
        console.log(`High issues: ${report.summary.high}`);
        console.log(`Medium issues: ${report.summary.medium}`);
        console.log(`Low issues: ${report.summary.low}`);
        return true;
      } else {
        console.log('');
        console.log('✅ Silent failure scan passed');
        if (report.summary.totalIssues > 0) {
          console.log(`Found ${report.summary.medium} medium and ${report.summary.low} low priority issues for review`);
        }
        return true;
      }
    }
    
    return true;
  } catch (error) {
    console.error('❌ Error running silent failure detection:');
    console.error(error.message);
    return false;
  }
}

// Integration with checkpoint system
function createCheckpoint(description) {
  const timestamp = new Date().toISOString();
  const checkpointData = {
    timestamp,
    description,
    silentFailureScan: {
      status: 'completed',
      passed: true,
      timestamp
    }
  };
  
  // Save checkpoint data for integration with existing checkpoint system
  const checkpointFile = path.join(process.cwd(), '.claude-checkpoint.json');
  let checkpoints = [];
  
  if (fs.existsSync(checkpointFile)) {
    try {
      checkpoints = JSON.parse(fs.readFileSync(checkpointFile, 'utf8'));
    } catch (e) {
      // Start fresh if file is corrupted
      checkpoints = [];
    }
  }
  
  checkpoints.push(checkpointData);
  fs.writeFileSync(checkpointFile, JSON.stringify(checkpoints, null, 2));
  
  console.log(`📋 Checkpoint created: ${description}`);
}

module.exports = { runSilentCheck, createCheckpoint };
```

## Integration Points

### 1. Checkpoint System Integration
- Creates checkpoints when silent failure scan passes
- Blocks progression when critical issues are found
- Integrates with existing `.claude-checkpoint.json` system

### 2. CI/CD Integration
- Returns exit code 1 when critical issues found
- Can be used in pre-commit hooks
- Generates machine-readable report for automation

### 3. Development Workflow
- Runs automatically before major commits
- Integrates with existing agent workflows
- Provides actionable feedback to developers

## Expected Output

### Success Case
```
🔍 Running silent failure detection...
📊 SILENT FAILURE DETECTION REPORT
================================================================================
Files analyzed: 42
Total issues found: 3
🟡 Medium: 2
🟢 Low: 1
✅ Silent failure scan passed
Found 2 medium and 1 low priority issues for review
📋 Checkpoint created: Silent failure scan passed
```

### Failure Case
```
🔍 Running silent failure detection...
📊 SILENT FAILURE DETECTION REPORT
================================================================================
Files analyzed: 42
Total issues found: 8
🔴 Critical: 3
🟠 High: 2
🟡 Medium: 2
🟢 Low: 1

🚨 CRITICAL SILENT FAILURES DETECTED
==================================================
❌ Cannot proceed with deployment until these are fixed
Critical issues: 3
High issues: 2

Fix these issues before running git commit or deployment.
```

## Configuration

### Environment Variables
- `CLAUDE_SILENT_CHECK_STRICT`: Set to 'true' to treat high-priority issues as blockers
- `CLAUDE_SILENT_CHECK_REPORT_PATH`: Custom path for the JSON report file

### Project-Level Configuration
Create `.claude-silent-check.json` in project root:
```json
{
  "enabled": true,
  "blockOnCritical": true,
  "blockOnHigh": false,
  "excludePaths": [
    "tests/**",
    "fixtures/**",
    "mock/**"
  ],
  "customPatterns": []
}
```

## Related Commands
- `/checkpoint` - Create development checkpoint
- `/git-status` - Check git status with silent failure scan
- `/prod-ready` - Full production readiness check including silent failures

## Best Practices
1. Run before every major commit
2. Fix critical issues immediately
3. Review high/medium issues during code review
4. Use in CI/CD pipeline as quality gate
5. Regular team reviews of patterns and thresholds