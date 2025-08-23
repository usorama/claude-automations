# Week 2 Implementation Tasks - Silent Failure Prevention & Code Intelligence

## Overview
This document contains the complete implementation plan for:
1. Week 2 of Silent Failure Prevention using GitHub Actions (replacing git hooks)
2. Code Intelligence Manifest System for providing context to all Claude Code agents

## Prerequisites
- INTEGRATION_PLAN.md already implemented Week 1 tasks
- GitHub repository with Actions enabled
- Claude Code with latest version
- Access to ~/.claude-code-docs for documentation reference

---

## PART 1: WEEK 2 - GITHUB ACTIONS AUTOMATION

### Research Context Embedded
- **GitHub Actions Claude Code Integration**: `anthropics/claude-code-action@beta` available
- **Security Review Action**: `anthropics/claude-code-security-review@main` exists
- **Setup Method**: Run `/install-github-app` in Claude Code
- **Permissions Required**: `pull-requests: write`, `checks: write`, `contents: read`
- **No IDE integration needed** - GitHub Actions better than local git hooks

### Task 1.1: Create Silent Failure Detection GitHub Action
**File**: `.github/workflows/silent-failure-prevention.yml`

```yaml
name: Silent Failure Prevention Pipeline
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  detect-silent-failures:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      checks: write
      contents: read
    
    steps:
      - name: Checkout PR Branch
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Environment
        run: |
          npm install -g ts-node typescript
          npm install glob
      
      - name: Copy Detector Script
        run: |
          mkdir -p .github/scripts
          cp ~/.claude/process-templates-n-prompts/silent-failures/silent-failure-detector.ts .github/scripts/
      
      - name: Run Silent Failure Detection
        id: detection
        run: |
          npx ts-node .github/scripts/silent-failure-detector.ts .
          echo "report=$(cat silent-failures-report.json | jq -c .)" >> $GITHUB_OUTPUT
      
      - name: Analyze with Claude
        if: always()
        uses: anthropics/claude-code-action@beta
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Analyze the silent failure detection report.
            If CRITICAL issues exist:
            - Comment specific fixes on the PR
            - Set status to FAILED
            If HIGH issues exist:
            - Set status to WARNING
            - Suggest improvements
```

### Task 1.2: Create Auto-Fix Workflow
**File**: `.github/workflows/auto-fix-silent-failures.yml`

```yaml
name: Auto-Fix Silent Failures
on:
  issue_comment:
    types: [created]

jobs:
  auto-fix:
    if: contains(github.event.comment.body, '@claude fix-silent-failures')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v4
      - name: Auto-Fix with Claude
        uses: anthropics/claude-code-action@beta
        with:
          prompt: |
            Read silent-failures-report.json
            Fix all CRITICAL issues:
            - Empty catch blocks: add proper error propagation
            - Mock data: replace with real implementations
            - Swallowed errors: add error handling
            Commit fixes with message: "fix: resolve silent failures"
```

### Task 1.3: Update Local Hooks for PR Creation
**File**: `~/.claude/hooks/pr-creation-hook.py`

```python
#!/usr/bin/env python3
import subprocess
import json

def auto_create_pr_on_feature_complete():
    """
    Creates PR when todo list complete or session ending
    """
    # Check if all todos complete
    todos = read_todo_state()
    if all(t['status'] == 'completed' for t in todos):
        create_pr()

def create_pr():
    subprocess.run([
        "gh", "pr", "create",
        "--title", generate_pr_title(),
        "--body", generate_pr_body(),
        "--label", "auto-generated"
    ])
```

### Task 1.4: Configure Auto-Commit Strategy
**File**: `~/.claude/hooks/auto-checkpoint-hook.py`

```python
#!/usr/bin/env python3
import time
import subprocess

CHECKPOINT_INTERVAL = 1800  # 30 minutes

def create_checkpoint_commit():
    """
    Auto-commits every 30 minutes or after major operations
    """
    changes = subprocess.check_output(["git", "status", "--porcelain"])
    if changes:
        message = generate_semantic_commit_message(changes)
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"{message}\n\n🔄 Auto-checkpoint"])
```

### Task 1.5: Setup GitHub Repository Settings
- [ ] Add `ANTHROPIC_API_KEY` to GitHub Secrets
- [ ] Enable required status checks for PR merging
- [ ] Configure branch protection rules
- [ ] Set up webhook for local Claude Code notifications

---

## PART 2: CODE INTELLIGENCE MANIFEST SYSTEM

### Research Context Embedded
- **TypeScript Compiler API**: Use `ts-morph` for AST analysis
- **API Extractor**: Microsoft tool for analyzing exports
- **Reference Syntax**: Use `@path/to/file` in CLAUDE.md
- **Max Import Depth**: 5 hops for recursive imports
- **Tools Available**: TypeDoc, dependency-cruiser, ts-morph

### Task 2.1: Create Manifest Directory Structure
```bash
mkdir -p ~/.claude/manifests
touch ~/.claude/manifests/CODEBASE_MANIFEST.yaml
touch ~/.claude/manifests/FUNCTION_REGISTRY.md
touch ~/.claude/manifests/EXPORT_REGISTRY.json
touch ~/.claude/manifests/IMPORT_GRAPH.yaml
touch ~/.claude/manifests/TECH_STACK.json
touch ~/.claude/manifests/CODE_PATTERNS.md
touch ~/.claude/manifests/DECISIONS_LOG.md
touch ~/.claude/manifests/API_SURFACE.json
```

### Task 2.2: Create Manifest Generator Script
**File**: `scripts/generate-manifests.ts`

```typescript
import { Project, Node, SyntaxKind } from 'ts-morph';
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

class ManifestGenerator {
  private project: Project;
  
  constructor() {
    this.project = new Project({
      tsConfigFilePath: './tsconfig.json'
    });
  }
  
  async generateAll() {
    const manifest = {
      project: {
        name: this.getPackageJson().name,
        version: this.getPackageJson().version,
        language: 'TypeScript',
        framework: this.detectFramework()
      },
      statistics: {
        total_functions: this.countFunctions(),
        total_exports: this.countExports(),
        async_functions: this.countAsyncFunctions()
      },
      key_modules: this.scanModules(),
      patterns: this.detectPatterns(),
      references: {
        functions: '@.claude/manifests/FUNCTION_REGISTRY.md',
        exports: '@.claude/manifests/EXPORT_REGISTRY.json',
        decisions: '@.claude/manifests/DECISIONS_LOG.md'
      }
    };
    
    // Write all manifests
    fs.writeFileSync('.claude/manifests/CODEBASE_MANIFEST.yaml', yaml.dump(manifest));
    await this.generateFunctionRegistry();
    await this.generateExportRegistry();
    await this.generateImportGraph();
  }
  
  private generateFunctionRegistry() {
    let markdown = '# Function Registry\\n\\n';
    
    this.project.getSourceFiles().forEach(file => {
      const functions = file.getFunctions();
      if (functions.length > 0) {
        markdown += `## ${file.getBaseName()}\\n\\n`;
        
        functions.forEach(func => {
          const name = func.getName() || 'anonymous';
          const signature = func.getSignature().getDeclaration().getText();
          const lineNumber = func.getStartLineNumber();
          
          markdown += `### ${name}\\n`;
          markdown += `- **Location**: \`${file.getFilePath()}:${lineNumber}\`\\n`;
          markdown += `- **Signature**: \`\`\`typescript\\n${signature}\\n\`\`\`\\n`;
          markdown += `- **Async**: ${func.isAsync()}\\n`;
          markdown += `- **Export**: ${func.isExported()}\\n\\n`;
        });
      }
    });
    
    fs.writeFileSync('.claude/manifests/FUNCTION_REGISTRY.md', markdown);
  }
  
  private generateExportRegistry() {
    const exports = {};
    
    this.project.getSourceFiles().forEach(file => {
      const filePath = file.getFilePath();
      const fileExports = [];
      
      file.getExportedDeclarations().forEach((declarations, name) => {
        fileExports.push({
          name,
          kind: declarations[0].getKindName(),
          line: declarations[0].getStartLineNumber()
        });
      });
      
      if (fileExports.length > 0) {
        exports[filePath] = fileExports;
      }
    });
    
    fs.writeFileSync('.claude/manifests/EXPORT_REGISTRY.json', JSON.stringify(exports, null, 2));
  }
}

// Run generator
new ManifestGenerator().generateAll();
```

### Task 2.3: Create GitHub Action for Manifest Generation
**File**: `.github/workflows/generate-manifests.yml`

```yaml
name: Generate Code Intelligence Manifests
on:
  push:
    branches: [main, develop]
  pull_request:
    types: [opened, synchronize]

jobs:
  generate-manifests:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Dependencies
        run: |
          npm install ts-morph typescript js-yaml
          npm install -g @microsoft/api-extractor
      
      - name: Generate Manifests
        run: npx ts-node scripts/generate-manifests.ts
      
      - name: Upload Manifests as Artifact
        uses: actions/upload-artifact@v3
        with:
          name: code-manifests-${{ github.event.pull_request.number || github.sha }}
          path: .claude/manifests/
      
      - name: Commit Manifests (if main branch)
        if: github.ref == 'refs/heads/main'
        run: |
          git config user.name "Manifest Bot"
          git config user.email "bot@example.com"
          git add .claude/manifests/
          git commit -m "📚 Update code intelligence manifests" || true
          git push || true
```

### Task 2.4: Update CLAUDE.md with References
**File**: `CLAUDE.md` (append to existing)

```markdown
## Code Intelligence System
All agents MUST read these manifests before implementation:
@.claude/manifests/CODEBASE_MANIFEST.yaml
@.claude/manifests/FUNCTION_REGISTRY.md
@.claude/manifests/EXPORT_REGISTRY.json
@.claude/manifests/CODE_PATTERNS.md

## Silent Failure Prevention
@.claude/process-templates-n-prompts/silent-failures/INTEGRATION_PLAN.md
```

### Task 2.5: Create Pre-Agent Context Hook
**File**: `~/.claude/hooks/pre-agent-context.py`

```python
#!/usr/bin/env python3
import subprocess
import json
import os

def inject_manifest_context():
    """
    Runs before any engineering agent to provide context
    """
    # Check if manifests exist locally
    manifest_dir = '.claude/manifests'
    
    if not os.path.exists(manifest_dir):
        # Try to download from latest PR
        try:
            pr_number = subprocess.check_output([
                "gh", "pr", "view", "--json", "number", "-q", ".number"
            ]).strip()
            
            if pr_number:
                subprocess.run([
                    "gh", "run", "download", "--name",
                    f"code-manifests-{pr_number}",
                    "--dir", manifest_dir
                ])
        except:
            print("⚠️ No manifests available. Generating local manifests...")
            subprocess.run(["npx", "ts-node", "scripts/generate-manifests.ts"])
    
    print("✅ Code intelligence manifests loaded")
```

### Task 2.6: Update Agent Templates
**For each agent in** `~/.claude/agents/`:

Add to agent prompt:
```markdown
MANDATORY CONTEXT CHECK:
Before writing ANY code, you MUST read:
1. @.claude/manifests/FUNCTION_REGISTRY.md - Check for existing functions
2. @.claude/manifests/EXPORT_REGISTRY.json - Use correct imports
3. @.claude/manifests/CODE_PATTERNS.md - Follow established patterns

NEVER create duplicate functions. ALWAYS reuse existing exports.
```

### Task 2.7: Create Manifest Validation Script
**File**: `scripts/validate-manifests.ts`

```typescript
// Validates that new code uses existing functions from manifests
import * as fs from 'fs';

function validateCodeAgainstManifests(newCode: string) {
  const functionRegistry = fs.readFileSync('.claude/manifests/FUNCTION_REGISTRY.md', 'utf-8');
  const exportRegistry = JSON.parse(fs.readFileSync('.claude/manifests/EXPORT_REGISTRY.json', 'utf-8'));
  
  // Check for duplicate function definitions
  // Check for incorrect imports
  // Check for pattern violations
  
  return {
    duplicates: [],
    incorrectImports: [],
    patternViolations: []
  };
}
```

---

## Implementation Order

### Phase 1: Foundation (Day 1)
1. [ ] Task 2.1 - Create manifest directory structure
2. [ ] Task 2.2 - Create manifest generator script
3. [ ] Task 2.4 - Update CLAUDE.md with references

### Phase 2: GitHub Actions (Day 2)
4. [ ] Task 1.1 - Create silent failure detection action
5. [ ] Task 1.2 - Create auto-fix workflow
6. [ ] Task 2.3 - Create manifest generation action
7. [ ] Task 1.5 - Configure GitHub repository settings

### Phase 3: Local Integration (Day 3)
8. [ ] Task 1.3 - Update local hooks for PR creation
9. [ ] Task 1.4 - Configure auto-commit strategy
10. [ ] Task 2.5 - Create pre-agent context hook

### Phase 4: Agent Updates (Day 4)
11. [ ] Task 2.6 - Update all agent templates
12. [ ] Task 2.7 - Create manifest validation script

### Phase 5: Testing & Refinement (Day 5-6)
13. [ ] Test silent failure detection on real PRs
14. [ ] Verify manifest generation accuracy
15. [ ] Test auto-fix capabilities
16. [ ] Validate agent context usage

---

## Success Criteria

### Silent Failure Prevention
- [ ] Every PR automatically scanned for silent failures
- [ ] Critical issues block PR merging
- [ ] Auto-fix attempts for common patterns
- [ ] No manual git hooks needed

### Code Intelligence
- [ ] Manifests auto-generate on every PR
- [ ] Agents read and use manifest context
- [ ] No duplicate functions created
- [ ] Correct imports used automatically

---

## Notes & References

### Documentation to Check
- Check `~/.claude-code-docs/` for latest Claude Code features
- Reference GitHub Actions docs for troubleshooting
- Use `/install-github-app` command for initial setup

### Key Research Findings
1. **TypeScript Compiler API**: ts-morph is best for AST analysis
2. **GitHub Actions**: Better than git hooks - centralized, unavoidable
3. **Claude @references**: Max 5 hops depth, not evaluated in code blocks
4. **Manifest Format**: YAML for configs, JSON for data, MD for documentation

### Rollback Safety
- PRs are isolated branches - safe for automation
- No automated changes to main branch
- All fixes require PR review before merge
- User can always override with admin merge

---

## Implementation Prompt for New Chat

Copy and paste this to start implementation:

```
I need to implement Week 2 of the Silent Failure Prevention Integration Plan with the following specifications:

1. Use GitHub Actions instead of git hooks for automation
2. Implement Code Intelligence Manifest System for agent context
3. All details are in: @.claude/process-templates-n-prompts/silent-failures/WEEK2_IMPLEMENTATION_TASKS.md

Please start with Phase 1 tasks and work through them systematically. Use the embedded research context to avoid re-researching. Check ~/.claude-code-docs for any Claude Code specific features before implementation.

The goal is to create:
- Automated silent failure detection on every PR
- Auto-generated code manifests for agent context
- Self-healing system that fixes issues automatically

Begin implementation now.
```