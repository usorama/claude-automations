# /init-project Command - Intelligent Project Initialization

## Purpose
Smart project initialization with automatic greenfield/brownfield detection. Adapts workflow based on whether you're starting fresh or working with existing code.

## Usage
```bash
/init-project [options]
```

## Options
- `--brownfield` - Force brownfield mode (skip detection)
- `--skip-detection` - Skip auto-detection, default to greenfield
- `--force` - Skip confirmation prompts
- `--help` - Show help message

## Implementation

```javascript
const { execSync } = require('child_process');
const path = require('path');

function runInit(args = '') {
  const scriptPath = path.join(__dirname, 'init-project.js');
  
  try {
    // Run the initializer
    execSync(`node "${scriptPath}" ${args}`, {
      cwd: process.cwd(),
      stdio: 'inherit'
    });
    
    return true;
  } catch (error) {
    console.error('❌ Initialization failed:', error.message);
    return false;
  }
}

// Command handler
module.exports = {
  name: 'init-project',
  description: 'Initialize project with smart greenfield/brownfield detection',
  execute: (args) => {
    console.log('🚀 Initializing project with intelligent detection...\n');
    return runInit(args.join(' '));
  }
};
```

## Auto-Detection Logic

### Greenfield Indicators (New Project)
- Empty directory or only README/LICENSE
- No git repository or <5 commits
- Default scaffolding without custom code
- No business logic or real tests

### Brownfield Indicators (Existing Project)
- Git history with >10 commits
- Custom business logic files
- Real test files (not examples)
- Production configuration
- Database schemas/migrations
- Multiple contributors

## Workflow Differentiation

### Greenfield Workflow
**Focus:** "What should we build?"

1. Discovery & Requirements
2. Architecture Design
3. Implementation Planning
4. Build from scratch
5. Establish patterns

**Creates:**
- `discovery.md` - Problem and user definition
- `requirements.md` - Feature requirements
- `constraints.md` - Constraints we create
- `risks.md` - Unknown unknowns
- `decisions.md` - Architectural decisions

### Brownfield Workflow
**Focus:** "What do we have?"

1. System Assessment
2. Constraint Documentation
3. Enhancement Planning
4. Safe Implementation
5. Incremental improvement

**Creates:**
- `system-assessment.md` - Current state analysis
- `constraints-inventory.md` - Existing constraints
- `enhancement-plan.md` - Improvement strategy
- `risk-assessment.md` - Known issues
- `technical-debt.md` - Debt inventory

## Examples

### New Project
```bash
/init-project
# Output:
🔍 Analyzing project structure...
🌱 Detected: New Project (confidence: 95%)
   - Empty directory
   
✅ Proceed with greenfield workflow? (Y/n): Y

🌱 GREENFIELD PROJECT INITIALIZATION
Focus: "What should we build?"

📁 Created planning structure:
   .claude/
   ├── discovery.md
   ├── requirements.md
   ├── constraints.md
   ├── risks.md
   └── decisions.md
```

### Existing Project
```bash
/init-project
# Output:
🔍 Analyzing project structure...
🏗️ Detected: Existing Codebase (confidence: 87%)
   - 234 commits, 3 contributors
   - 47 source files
   - Custom business logic detected
   
✅ Proceed with brownfield workflow? (Y/n): Y

🏗️ BROWNFIELD PROJECT ASSESSMENT
Focus: "What do we have?"

📊 System Analysis Results:
   Language: JavaScript/TypeScript
   Framework: Next.js
   Architecture: MVC
   Test Coverage: 67%
   
📁 Created assessment structure:
   .claude/
   ├── system-assessment.md
   ├── constraints-inventory.md
   ├── enhancement-plan.md
   ├── risk-assessment.md
   └── technical-debt.md
```

### Force Brownfield Mode
```bash
/init-project --brownfield
# Skips detection, goes straight to brownfield workflow
# Useful when working on a module of a larger system
```

## Integration Points

### With BMad Method
- Greenfield → Full BMad workflow from Phase 0
- Brownfield → Choose enhancement approach:
  - Single story (small change)
  - Epic (medium enhancement)
  - Major project (large refactor)

### With Other Commands
After `/init-project`, use:
- **Greenfield:** `/0.1discover`, `/0.2define`, `/0.3validate`
- **Brownfield:** `/assess`, `/constraints`, `/enhance`

## Best Practices

1. **Trust auto-detection** - It's accurate 90% of the time
2. **Review generated docs** - Fill them out for better context
3. **Start small in brownfield** - Build confidence first
4. **Document constraints early** - Saves pain later
5. **Use appropriate workflow** - Don't force greenfield on legacy code

## Notes
- Detection is non-destructive (read-only analysis)
- Creates `.claude/project-config.json` to save decision
- All generated documents are templates to be filled out
- Can be re-run safely (won't overwrite existing docs)