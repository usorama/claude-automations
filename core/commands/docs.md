---
description: Execute comprehensive documentation using the documentation framework
argument-hint: [project-path]
---

# Documentation Framework Execution

## Initialize Documentation Framework

Use the comprehensive documentation framework from ~/.claude/process-templates-n-prompts/documentation/

### Step 1: Check for Existing Documentation Infrastructure
First, check if `.claude/docs/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If documentation framework doesn't exist in the project:
```bash
mkdir -p .claude/docs
cp ~/.claude/process-templates-n-prompts/documentation/*.md .claude/docs/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read documentation-prompt.md** - Understand the documentation philosophy and best practices
   - Focus on user-centered documentation and information architecture
   - Review technical writing standards and accessibility guidelines
   - Understand documentation maintenance and versioning strategies

2. **Load documentation-template.md** - Use as the structure for documentation organization
   - Reference for document structure templates
   - Use style guide and formatting conventions
   - Follow API documentation and code comment templates
   - Use user guide and tutorial formats

3. **Follow documentation-checklist.md** - Execute phases systematically
   - Start with Phase 0: Documentation Audit & Planning
   - Check off items as completed
   - Document information architecture
   - Track documentation quality and coverage metrics

## Execution Instructions

### Phase 0: Documentation Audit & Planning (MANDATORY FIRST)
- Audit existing documentation and identify gaps
- Define target audiences and their information needs
- Map documentation types and organizational structure
- Review style guides and formatting standards
- Assess current tools and publishing workflows
- Establish documentation quality and maintenance standards

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Information Architecture & Content Strategy
- Phase 2: Content Creation & Technical Writing
- Phase 3: Code Documentation & API References
- Phase 4: User Guides & Tutorial Development
- Phase 5: Documentation Testing & Review
- Phase 6: Publishing & Distribution
- Phase 7: Maintenance & Continuous Improvement

## Key Principles

1. **ALWAYS write for your audience, not for yourself**
2. **Structure information logically with clear navigation**
3. **Keep documentation current and synchronized with code**
4. **Use consistent style, tone, and formatting**
5. **Include practical examples and real-world scenarios**
6. **Test documentation with actual users**

## Documentation Goals
- Comprehensive coverage of all features and APIs
- Clear information architecture with intuitive navigation
- Consistent style and formatting across all documents
- Practical examples and step-by-step tutorials
- Accessible content that serves diverse user needs
- Automated publishing and maintenance workflows

## Progress Tracking
Update the documentation-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. information-architecture.md - Documentation structure and organization
2. style-guide.md - Writing standards and formatting conventions
3. api-documentation/ - Comprehensive API reference
4. user-guides/ - End-user documentation and tutorials
5. developer-docs/ - Technical documentation for contributors
6. maintenance-plan.md - Documentation update and review procedures
7. publishing-workflow.md - Content publishing and distribution setup
8. CHANGELOG.md - Document all documentation changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Good documentation is like a conversation with your future self and your users. Write clearly, organize thoughtfully, maintain diligently.