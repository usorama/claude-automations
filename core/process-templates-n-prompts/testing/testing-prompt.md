# COMPREHENSIVE E2E TESTING PROMPT FOR CLAUDE CODE

## 📁 REQUIRED TESTING ARTIFACTS
Before beginning ANY testing work, Claude Code MUST:

### 1. CHECK for Testing Framework Files
Look for these files in the following locations (in order):
```
1. .claude/testing/testing-template.md
2. .claude/testing/testing-checklist.md
3. ./testing-template.md
4. ./testing-checklist.md
5. ./docs/testing/testing-template.md
6. ./docs/testing/testing-checklist.md
```

### 2. IF Testing Framework Files NOT Found:
Create them using these commands:
```bash
# Create .claude directory structure
mkdir -p .claude/testing

# Download or create the files
# testing-template.md - Provides structure for all test types
# testing-checklist.md - Provides step-by-step execution guide
```

### 3. USE the Testing Framework:
- **testing-template.md**: Use as the STRUCTURE for organizing tests
- **testing-checklist.md**: Use as the EXECUTION guide, checking off items as completed
- **This prompt**: Provides the PHILOSOPHY and approach

## 🎯 HOW TO USE THIS FRAMEWORK

### Step 1: Initialize Testing Framework
```bash
# First, always check for and load the testing artifacts
if [ -f ".claude/testing/testing-checklist.md" ]; then
  echo "Found testing checklist - loading..."
  # READ the checklist and start from Phase 0
else
  echo "Creating testing framework files..."
  # CREATE the necessary files in .claude/testing/
fi
```

### Step 2: Follow the Checklist Phases
Open `testing-checklist.md` and systematically work through:
- Phase 0: Discovery & Inventory
- Phase 1: Preparation & Analysis  
- Phase 2: Test Planning
- Phase 3: Implementation
- Phase 4: Test Execution
- Phase 5: Quality Validation
- Phase 6: Reporting
- Phase 7: Continuous Improvement

### Step 3: Use the Template for Structure
Reference `testing-template.md` for:
- Test file structures
- Naming conventions
- Test category templates
- Report formats
- Coverage metrics structure

### Step 4: Document Progress
Update the checklist as you go:
```markdown
- [x] Completed item
- [ ] Pending item
- [~] Partially complete
- [!] Blocked item
```

## OBJECTIVE
Execute comprehensive end-to-end testing with 100% coverage, zero technical debt, and evidence-based verification using Playwright and specialized testing tools for ANY project or application.

## 🚨 CRITICAL RULE: CHECK BEFORE CREATE
### MANDATORY: Artifact Discovery Protocol
Before creating ANY new file or artifact, you MUST:

1. **SEARCH for existing artifacts**:
   - [ ] Check for existing `testing-manifest.md` or similar files
   - [ ] Look for `test/`, `tests/`, `spec/`, `__tests__/` directories
   - [ ] Find existing `playwright.config.*` or test configurations
   - [ ] Locate any `coverage/` reports or directories
   - [ ] Search for `.claude/`, `claude.md`, or AI-specific configs
   - [ ] Check for existing CI/CD test workflows (`.github/workflows/`, `.gitlab-ci.yml`)

2. **ANALYZE what exists**:
   - [ ] Read and understand existing test structure
   - [ ] Identify gaps in current coverage
   - [ ] Note existing naming conventions
   - [ ] Understand current test patterns
   - [ ] Document what's working well
   - [ ] List what needs improvement

3. **INTEGRATE, don't duplicate**:
   - [ ] UPDATE existing manifests rather than creating new ones
   - [ ] EXTEND existing test suites rather than replacing
   - [ ] PRESERVE existing test data and fixtures
   - [ ] MAINTAIN compatibility with existing CI/CD
   - [ ] RESPECT existing folder structures and conventions
   - [ ] MERGE new requirements with existing documentation

4. **DECISION TREE**:
   ```
   IF artifact exists:
     -> READ it completely
     -> IDENTIFY gaps
     -> UPDATE with missing pieces
     -> VERSION the changes
   ELSE:
     -> CONFIRM no similar artifact exists
     -> CREATE new artifact
     -> FOLLOW project conventions
   ```

## WORKFLOW INTEGRATION

### When Starting a Testing Task:
```typescript
// Pseudo-code for Claude Code's workflow
async function initializeE2ETesting() {
  // 1. Load the testing framework
  const checklist = await loadFile('.claude/testing/testing-checklist.md');
  const template = await loadFile('.claude/testing/testing-template.md');
  
  // 2. Start with Phase 0 of checklist
  const discoveryPhase = parsePhase(checklist, 'PHASE 0');
  await executeDiscovery(discoveryPhase);
  
  // 3. Use template for creating test structures
  const testStructure = parseTemplate(template);
  await createTestFiles(testStructure);
  
  // 4. Continue through checklist phases
  for (const phase of checklist.phases) {
    await executePhase(phase);
    updateProgress(phase);
  }
}
```

## CORE REQUIREMENTS

### 1. THINKING PATTERN (MANDATORY)
Before ANY action, you MUST:
- **CONSULT** the testing-checklist.md for next steps
- **REFERENCE** the testing-template.md for structure
- **THINK** about what already exists in the codebase
- **THINK HARDER** about potential conflicts with existing infrastructure
- **ULTRATHINK** when dealing with complex scenarios
- Use the explore-plan-code-commit workflow strictly
- Never make assumptions - verify everything through evidence

### 2. EVIDENCE-BASED APPROACH
- **DISCOVER** existing test infrastructure first
- **READ** every file you reference - if you don't see it, it doesn't exist
- **VERIFY** all routes, imports, exports through actual code inspection
- **VALIDATE** container configurations by examining Docker/compose files
- **CHECK** UI components by analyzing actual component files
- **CONFIRM** all dependencies through package.json and lock files

### 3. MULTI-AGENT ORCHESTRATION
Delegate to specialized sub-agents:
- **discovery-agent**: Find all existing test artifacts FIRST
- **test-automator**: Create/update comprehensive test suites
- **qa-coordinator**: Manage testing strategy
- **ux-testing-agent**: Handle UI/UX and usability testing
- **accessibility-agent**: Ensure WCAG compliance
- **performance-engineer**: Profile and optimize
- **security-auditor**: Scan for vulnerabilities
- **dependency-validator**: Check all imports/exports
- **localization-tester**: Verify i18n/l10n support

### 4. COMPREHENSIVE TESTING SCOPE

#### 4.1 Infrastructure Testing
<infrastructure>
- Container orchestration validation
- Service communication verification
- Database connection testing
- API gateway validation
- Message queue verification
- Cache layer testing
- CDN functionality
- Load balancer health
</infrastructure>

#### 4.2 Application Testing
<application>
- Complete route coverage (100% endpoints)
- All user roles and permissions
- Critical user journeys
- Edge cases and error handling
- State management validation
- Data flow verification
- Business logic validation
- Performance benchmarks
</application>

#### 4.3 UI/UX Testing
<ui_ux>
- Visual regression testing
- Responsive design validation
- Cross-browser compatibility
- Touch/gesture interactions
- Keyboard navigation
- Focus management
- Animation performance
- Loading states
- Error states
- Empty states
- Micro-interactions
- Form usability
- Color contrast
- Typography readability
- Spacing consistency
</ui_ux>

#### 4.4 Accessibility Testing
<accessibility>
- WCAG 2.1 AA compliance
- Screen reader compatibility
- Keyboard-only navigation
- Focus indicators
- ARIA labels and roles
- Color contrast ratios
- Text alternatives
- Captions and transcripts
- Semantic HTML validation
</accessibility>

#### 4.5 Code Quality Testing
<quality>
- Zero duplicate code
- No missing routes or endpoints
- Correct import/export chains
- No stale or dead code
- No unused dependencies
- Proper error handling
- Memory leak detection
- Bundle size optimization
</quality>

#### 4.6 Localization Testing
<localization>
- Text translation coverage
- Date/time formatting
- Number formatting
- Currency display
- RTL/LTR support
- Character encoding
- Local regulations compliance
</localization>

## EXECUTION WORKFLOW

### Phase 0: DISCOVERY (MANDATORY FIRST STEP)
**→ Refer to testing-checklist.md Phase 0 for detailed steps**
```
1. Search for ALL existing test-related files
2. Document current test infrastructure
3. Identify test frameworks already in use
4. Map existing coverage reports
5. Review existing CI/CD pipelines
6. List all testing documentation found
```

### Phase 1: Analysis and Mapping
**→ Refer to testing-checklist.md Phase 1 for detailed steps**
```
1. Scan entire codebase structure
2. COMPARE with existing test coverage
3. Create/UPDATE dependency graph
4. Map all routes and endpoints
5. DIFF against existing test manifests
6. Document NEW requirements only
7. Identify UI/UX patterns
8. Map accessibility requirements
```

### Phase 2: Test Manifest Creation/Update
**→ Use testing-template.md for structure**
- IF `testing-manifest.md` exists:
  - APPEND new discoveries
  - UPDATE outdated sections
  - PRESERVE existing valid content
- ELSE create new with structure from template

### Phase 3: Test Implementation
**→ Use testing-template.md for test patterns**
- REUSE existing test helpers and utilities
- EXTEND existing page objects
- FOLLOW existing naming conventions
- BUILD ON existing fixtures

### Phase 4: Validation
**→ Follow testing-checklist.md Phase 4-7**
- Run ALL tests (existing + new)
- Compare coverage with baseline
- Verify improvement metrics
- Generate comprehensive reports

## FILE ORGANIZATION STRUCTURE

### Recommended Project Structure:
```
project-root/
├── .claude/
│   ├── testing/
│   │   ├── testing-template.md    # Test structure templates
│   │   ├── testing-checklist.md   # Execution checklist
│   │   └── testing-progress.md    # Progress tracking
│   └── commands/
│       └── test-commands.md       # Reusable test commands
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── visual/
│   ├── accessibility/
│   ├── performance/
│   └── security/
├── testing-manifest.md             # Living test documentation
└── coverage/
    └── reports/
```

## PROGRESS TRACKING

### Update testing-checklist.md with progress:
```markdown
## 📊 Current Progress
- Phase 0: ✅ Complete
- Phase 1: ✅ Complete  
- Phase 2: 🔄 In Progress (60%)
- Phase 3: ⏳ Pending
- Phase 4: ⏳ Pending
- Phase 5: ⏳ Pending
- Phase 6: ⏳ Pending
- Phase 7: ⏳ Pending

Last Updated: [timestamp]
```

## CRITICAL INSTRUCTIONS

⚠️ **DO NOT**:
- Start testing without loading the framework files
- Skip checklist phases
- Ignore the template structure
- Create tests without consulting the template
- Override existing configurations without analysis
- Make assumptions about file existence

✅ **ALWAYS**:
- Load testing-checklist.md and testing-template.md first
- Follow the checklist phases in order
- Use template structures for consistency
- Check for existing artifacts FIRST
- Document progress in the checklist
- Update the template with project-specific patterns

## ACTIVATION COMMAND
When ready to begin, execute:
```
load_testing_framework && discover_existing && ultrathink && follow_checklist_phases && use_template_structures && validate_coverage
```

## SUCCESS METRICS
Testing is complete when:
1. ✅ All checklist items are marked complete
2. ✅ All template sections are implemented
3. ✅ Coverage targets are achieved
4. ✅ Reports are generated
5. ✅ Documentation is updated

## VERSION CONTROL INTEGRATION
- Commit `.claude/testing/` files to version control
- Track checklist progress in commits
- Version template updates
- Document framework improvements

Remember: The testing-template.md provides the WHAT, the testing-checklist.md provides the HOW, and this prompt provides the WHY. Use all three together for comprehensive E2E testing success.
