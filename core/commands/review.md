---
description: Execute comprehensive code quality assessment using the code quality framework
argument-hint: [project-path]
---

# Code Quality Framework Execution

## Initialize Code Quality Framework

Use the comprehensive code quality framework from ~/.claude/process-templates-n-prompts/code-quality/

### Step 1: Check for Existing Code Quality Infrastructure
First, check if `.claude/quality/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If code quality framework doesn't exist in the project:
```bash
mkdir -p .claude/quality
cp ~/.claude/process-templates-n-prompts/code-quality/*.md .claude/quality/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read code-quality-prompt.md** - Understand the code quality philosophy and standards
   - Focus on clean code principles, maintainability, and technical debt management
   - Review static analysis, code review, and refactoring strategies
   - Understand quality gates and continuous quality improvement

2. **Load code-quality-template.md** - Use as the structure for quality documentation
   - Reference for code review checklist templates
   - Use quality metrics and reporting templates
   - Follow refactoring and improvement templates
   - Use quality gate configuration formats

3. **Follow code-quality-checklist.md** - Execute phases systematically
   - Start with Phase 0: Code Quality Assessment & Baseline
   - Check off items as completed
   - Document quality improvements and refactoring
   - Track quality metrics and technical debt reduction

## Execution Instructions

### Phase 0: Code Quality Assessment & Baseline (MANDATORY FIRST)
- Assess current code quality using static analysis tools
- Identify technical debt, code smells, and quality issues
- Document coding standards and style guide compliance
- Map code complexity, maintainability, and test coverage
- Review existing quality tools and CI/CD integration
- Establish quality baselines and improvement targets

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Static Analysis & Linting Configuration
- Phase 2: Code Review Process & Standards
- Phase 3: Refactoring & Technical Debt Reduction
- Phase 4: Test Coverage & Quality Improvement
- Phase 5: Documentation & Code Comments
- Phase 6: Quality Gates & CI/CD Integration
- Phase 7: Continuous Quality Monitoring & Improvement

## Key Principles

1. **ALWAYS prioritize readability and maintainability over cleverness**
2. **Implement automated quality checks in CI/CD pipelines**
3. **Establish clear coding standards and enforce them consistently**
4. **Regular refactoring to prevent technical debt accumulation**
5. **Comprehensive code review process with constructive feedback**
6. **Balance quality improvements with delivery commitments**

## Quality Goals
- Consistent coding standards and style across the codebase
- High test coverage with meaningful and maintainable tests
- Low code complexity and high maintainability scores
- Minimal technical debt and code smell violations
- Effective code review process with quality feedback
- Automated quality gates preventing quality regressions

## Progress Tracking
Update the code-quality-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. quality-assessment.md - Current code quality baseline and analysis
2. coding-standards.md - Project coding standards and style guide
3. static-analysis-config/ - Linting and static analysis tool configurations
4. code-review-checklist.md - Standardized code review process
5. refactoring-plan.md - Technical debt reduction and refactoring roadmap
6. quality-metrics.md - Code quality metrics and tracking dashboard
7. quality-gates.md - CI/CD quality gate configuration and thresholds
8. CHANGELOG.md - Document all code quality improvements

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Quality code is not an accident but a discipline. Write for humans, automate quality checks, refactor ruthlessly, review thoughtfully.