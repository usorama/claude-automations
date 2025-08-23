---
description: Execute comprehensive architecture design using the architecture framework
argument-hint: [project-path]
---

# Architecture Framework Execution

## Initialize Architecture Framework

Use the comprehensive architecture framework from ~/.claude/process-templates-n-prompts/architecture/

### Step 1: Check for Existing Architecture Documentation
First, check if `.claude/architecture/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If architecture framework doesn't exist in the project:
```bash
mkdir -p .claude/architecture
cp ~/.claude/process-templates-n-prompts/architecture/*.md .claude/architecture/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read architecture-prompt.md** - Understand the design philosophy and architectural principles
   - Focus on system design patterns and best practices
   - Review scalability and maintainability requirements
   - Understand the multi-layered architecture approach

2. **Load architecture-template.md** - Use as the structure for architectural documentation
   - Reference for component design structures
   - Use naming conventions from template
   - Follow architectural pattern templates
   - Use design documentation formats

3. **Follow architecture-checklist.md** - Execute phases systematically
   - Start with Phase 0: Requirements Analysis
   - Check off items as completed
   - Document design decisions
   - Track architectural metrics

## Execution Instructions

### Phase 0: Requirements Analysis (MANDATORY FIRST)
- Gather functional and non-functional requirements
- Identify system constraints and assumptions
- Document stakeholder needs and expectations
- Map quality attributes (performance, security, scalability)
- Review existing system architecture if any
- Document architectural context and boundaries

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Architecture Strategy & Planning
- Phase 2: System Design & Modeling
- Phase 3: Component Architecture Design
- Phase 4: Integration Architecture
- Phase 5: Quality Architecture Validation
- Phase 6: Architecture Documentation
- Phase 7: Architecture Governance & Evolution

## Key Principles

1. **ALWAYS analyze existing architecture before proposing changes**
2. **Design for scalability, maintainability, and extensibility**
3. **Document architectural decisions and trade-offs**
4. **Follow established architectural patterns and principles**
5. **Ensure alignment with business objectives**
6. **Plan for evolution and technical debt management**

## Architecture Goals
- Clear separation of concerns
- High cohesion, low coupling
- Scalable and performant design
- Security by design
- Maintainable and testable architecture
- Technology alignment with business strategy

## Progress Tracking
Update the architecture-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. architecture-overview.md - High-level system design
2. component-diagrams/ - Detailed component designs
3. architecture-decisions.md - ADR (Architecture Decision Records)
4. system-context.md - System boundaries and integrations
5. quality-attributes.md - Non-functional requirements mapping
6. technology-stack.md - Technology choices and rationale
7. deployment-architecture.md - Infrastructure and deployment design
8. CHANGELOG.md - Document all architectural changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Good architecture is invisible when it works, but critical when it doesn't. Design thoughtfully, document thoroughly, plan for change.