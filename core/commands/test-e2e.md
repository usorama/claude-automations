---
description: Execute comprehensive E2E testing using the testing framework
argument-hint: [project-path]
---

# E2E Testing Framework Execution

## Initialize Testing Framework

Use the comprehensive E2E testing framework from ~/.claude/process-templates-n-prompts/

### Step 1: Check for Existing Testing Infrastructure
First, check if `.claude/testing/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If testing framework doesn't exist in the project:
```bash
mkdir -p .claude/testing
cp ~/.claude/process-templates-n-prompts/testing-*.md .claude/testing/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read testing-prompt.md** - Understand the philosophy, approach, and core requirements
   - Pay special attention to the "Check Before Create" rule
   - Understand the thinking patterns (THINK, THINK HARDER, ULTRATHINK)
   - Review the multi-agent orchestration approach

2. **Load testing-template.md** - Use as the structure for organizing all tests
   - Reference for test file structures
   - Use naming conventions from template
   - Follow test category templates
   - Use report formats from template

3. **Follow testing-checklist.md** - Execute phases systematically
   - Start with Phase 0: Discovery & Inventory
   - Check off items as completed
   - Document progress in the checklist
   - Track metrics as specified

## Execution Instructions

### Phase 0: Discovery (MANDATORY FIRST)
- Search for ALL existing test-related files
- Document current test infrastructure  
- Identify test frameworks already in use
- Map existing coverage reports
- Review existing CI/CD pipelines
- List all testing documentation found

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Preparation & Analysis
- Phase 2: Test Planning
- Phase 3: Implementation
- Phase 4: Test Execution
- Phase 5: Quality Validation
- Phase 6: Reporting
- Phase 7: Continuous Improvement

## Key Principles

1. **ALWAYS check what exists before creating anything new**
2. **Preserve valuable existing tests and infrastructure**
3. **Update and extend rather than replace**
4. **Document all changes made**
5. **Maintain backward compatibility**
6. **Test all aspects comprehensively (functional, visual, accessibility, performance, security)**

## Coverage Goals
- 100% route/endpoint coverage
- Complete UI/UX testing including visual regression
- Full accessibility compliance (WCAG 2.1 AA)
- Performance benchmarks met
- Security scanning passed
- Zero technical debt

## Progress Tracking
Update the testing-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. testing-manifest.md - Living test documentation
2. test-results.json - Detailed results
3. coverage-report.html - Visual coverage report
4. accessibility-report.html - WCAG compliance
5. visual-regression-report.html - UI consistency
6. performance-metrics.json - Performance data
7. security-scan-report.json - Vulnerability assessment
8. CHANGELOG.md - Document all changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Every untested path is a potential failure point. Be meticulous, be thorough, be evidence-based.
